# %%
import asyncio
import os
from PIL import Image, ImageGrab
from tapo import ApiClient
from tapo.requests import Color
from io import BytesIO
import numpy as np
from imagedominantcolour import DominantColour
from time import sleep,time
import numexpr as ne
import timeit
from mss import mss
import pyautogui
import dxcam

# %%
async def toggle_bulb(device):
    device_info = await device.get_device_info()
    if device_info.device_on == True:
        print("Device is on. Turning it off...")
        await device.off()
    elif device_info.device_on == False:
        print("Device is off. Turning it on...")
        await device.on()
    else:
        print("Cant Toggle")


# %%
def bincount_numexpr_app(a):
    a2D = a.reshape(-1,a.shape[-1])
    col_range = (256, 256, 256) # generically : a2D.max(0)+1
    eval_params = {'a0':a2D[:,0],'a1':a2D[:,1],'a2':a2D[:,2],
                   's0':col_range[0],'s1':col_range[1]}
    a1D = ne.evaluate('a0*s0*s1+a1*s0+a2',eval_params)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


# %%
def bincount_app(a):
    a2D = a.reshape(-1,a.shape[-1])
    col_range = (256, 256, 256) # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(a2D.T, col_range)
    return np.unravel_index(np.bincount(a1D).argmax(), col_range)

# %%
# list_of_colors = [[255,0,0],[150,33,77],[75,99,23],[45,88,250],[250,0,255]]
def closest(colors,color):
    list_of_colors_names = [Color.CoolWhite,Color.Daylight,Color.Ivory,Color.WarmWhite,Color.Incandescent,Color.Candlelight,Color.Snow,Color.GhostWhite,Color.AliceBlue,Color.LightGoldenrod,Color.LemonChiffon,Color.AntiqueWhite,Color.Gold,Color.Peru,Color.Chocolate,Color.SandyBrown,Color.Coral,Color.Pumpkin,Color.Tomato,Color.Vermilion,Color.OrangeRed,Color.Pink,Color.Crimson,Color.DarkRed,Color.HotPink,Color.Smitten,Color.MediumPurple,Color.BlueViolet,Color.Indigo,Color.LightSkyBlue,Color.CornflowerBlue,Color.Ultramarine,Color.DeepSkyBlue,Color.Azure,Color.NavyBlue,Color.LightTurquoise,Color.Aquamarine,Color.Turquoise,Color.LightGreen,Color.Lime]
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))[0][0]
    # print(index_of_smallest[0][0])
    smallest_distance = list_of_colors_names[index_of_smallest]
    return smallest_distance


# %%
def average_color_numpy(image_array):
    avg_color_per_row = np.average(image_array, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return tuple(avg_color.astype(int))

# %%
async def gamer_mode(device):
    # color_map = {'maroon':[128,0,0],'dark red':(139,0,0),'brown':(165,42,42),'firebrick':(178,34,34),'crimson':(220,20,60),'red':(255,0,0),'tomato':(255,99,71),'coral':(255,127,80),'indian red':(205,92,92),'light coral':(240,128,128),'dark salmon':(233,150,122),'salmon':(250,128,114),'light salmon':(255,160,122),'orange red':(255,69,0),'dark orange':(255,140,0),'orange':(255,165,0),'gold':(255,215,0),'dark golden rod':(184,134,11),'golden rod':(218,165,32),'pale golden rod':(238,232,170),'dark khaki':(189,183,107),'khaki':(240,230,140),'olive':(128,128,0),'yellow':(255,255,0),'yellow green':(154,205,50),'dark olive green':(85,107,47),'olive drab':(107,142,35),'lawn green':(124,252,0),'chartreuse':(127,255,0),'green yellow':(173,255,47),'dark green':(0,100,0),'green':(0,128,0),'forest green':(34,139,34),'lime':(0,255,0),'lime green':(50,205,50),'light green':(144,238,144),'pale green':(152,251,152),'dark sea green':(143,188,143),'medium spring green':(0,250,154),'spring green':(0,255,127),'sea green':(46,139,87),'medium aqua marine':(102,205,170),'medium sea green':(60,179,113),'light sea green':(32,178,170),'dark slate gray':(47,79,79),'teal':(0,128,128),'dark cyan':(0,139,139),'aqua':(0,255,255),'cyan':(0,255,255),'light cyan':(224,255,255),'dark turquoise':(0,206,209),'turquoise':(64,224,208),'medium turquoise':(72,209,204),'pale turquoise':(175,238,238),'aqua marine':(127,255,212),'powder blue':(176,224,230),'cadet blue':(95,158,160),'steel blue':(70,130,180),'corn flower blue':(100,149,237),'deep sky blue':(0,191,255),'dodger blue':(30,144,255),'light blue':(173,216,230),'sky blue':(135,206,235),'light sky blue':(135,206,250),'midnight blue':(25,25,112),'navy':(0,0,128),'dark blue':(0,0,139),'medium blue':(0,0,205),'blue':(0,0,255),'royal blue':(65,105,225),'blue violet':(138,43,226),'indigo':(75,0,130),'dark slate blue':(72,61,139),'slate blue':(106,90,205),'medium slate blue':(123,104,238),'medium purple':(147,112,219),'dark magenta':(139,0,139),'dark violet':(148,0,211),'dark orchid':(153,50,204),'medium orchid':(186,85,211),'purple':(128,0,128),'thistle':(216,191,216),'plum':(221,160,221),'violet':(238,130,238),'magenta / fuchsia':(255,0,255),'orchid':(218,112,214),'medium violet red':(199,21,133),'pale violet red':(219,112,147),'deep pink':(255,20,147),'hot pink':(255,105,180),'light pink':(255,182,193),'pink':(255,192,203),'antique white':(250,235,215),'beige':(245,245,220),'bisque':(255,228,196),'blanched almond':(255,235,205),'wheat':(245,222,179),'corn silk':(255,248,220),'lemon chiffon':(255,250,205),'light golden rod yellow':(250,250,210),'light yellow':(255,255,224),'saddle brown':(139,69,19),'sienna':(160,82,45),'chocolate':(210,105,30),'peru':(205,133,63),'sandy brown':(244,164,96),'burly wood':(222,184,135),'tan':(210,180,140),'rosy brown':(188,143,143),'moccasin':(255,228,181),'navajo white':(255,222,173),'peach puff':(255,218,185),'misty rose':(255,228,225),'lavender blush':(255,240,245),'linen':(250,240,230),'old lace':(253,245,230),'papaya whip':(255,239,213),'sea shell':(255,245,238),'mint cream':(245,255,250),'slate gray':(112,128,144),'light slate gray':(119,136,153),'light steel blue':(176,196,222),'lavender':(230,230,250),'floral white':(255,250,240),'alice blue':(240,248,255),'ghost white':(248,248,255),'honeydew':(240,255,240),'ivory':(255,255,240),'azure':(240,255,255),'snow':(255,250,250),'black':(0,0,0),'dim gray / dim grey':(105,105,105),'gray / grey':(128,128,128),'dark gray / dark grey':(169,169,169),'silver':(192,192,192),'light gray / light grey':(211,211,211),'gainsboro':(220,220,220),'white smoke':(245,245,245),'white':(255,255,255)}
    list_of_colors = [[255,255,255],[254,223,203],[255,255,240],[253, 244, 220],[255,245,213],[255,255,205],[255,250,250],[248,248,255],[240,248,255],[250,250,210],[255,250,205],[250,235,215],[255,215,0],[205,133,63],[210,105,30],[244,164,96],[255,127,80],[255,117,24],[255,99,71],[204,71,75],[255,69,0],[255,192,203],[220,20,60],[139,0,0],[255,105,180],[200,5,134],[199,21,133],[138,43,226],[75,0,130],[135,206,250],[100,149,237],[5,102,245],[0,191,255],[240,255,255],[0,0,128],[175,238,238],[127,255,212],[64,224,208],[144,238,144],[0,255,0]]
    camera = dxcam.create()
    
    while(True):
        # image_1 = ImageGrab.grab() #Define an area to capture.
        # image = image_1.resize((256, 256), Image.BILINEAR)
        # buf = BytesIO()
        # image.save(buf, format='JPEG')
        # buf.seek(0)
        # col_val = DominantColour(buf)
        

        frame = camera.grab()
        if(frame is not None):
                # image = Image.fromarray(frame)
                # buf = BytesIO()
                # image.save(buf, format='JPEG')
                # buf.seek(0)
                # col_val = DominantColour(buf)
                color = average_color_numpy(frame)


        # mss approach-------------------------------------
                # with mss.mss() as sct:
                #     monitor = sct.monitors[0]
                #     im = sct.grab(monitor)           
                # buf = BytesIO()
                # buf.write(mss.tools.to_png(im.rgb, im.size))          
                # buf.seek(0)
                # col_val = DominantColour(buf)


        #bincount approach--------------------------------------------------
                # a = np.array(image)
                # col_val =timeit.timeit(bincount_numexpr_app(a)) 
                #col_val =bincount_app(a) 
                # color = [col_val[0], col_val[1], col_val[2]]
                
        #pillow approach
                # img = image.resize((1, 1), resample=0)
                # col_val = img.getpixel((0, 0))
                # color = [col_val[0], col_val[1], col_val[2]]

                # color = [col_val.r, col_val.g, col_val.b]
                final_color = closest(list_of_colors, color)
                await device.set_color(final_color)


# %%
def capture_screenshot():
    with mss() as sct:
            monitor = sct.monitors[1]
            im = sct.grab(monitor)
            return im

# %%
async def gamer_mode_timer(device):
    # color_map = {'maroon':[128,0,0],'dark red':(139,0,0),'brown':(165,42,42),'firebrick':(178,34,34),'crimson':(220,20,60),'red':(255,0,0),'tomato':(255,99,71),'coral':(255,127,80),'indian red':(205,92,92),'light coral':(240,128,128),'dark salmon':(233,150,122),'salmon':(250,128,114),'light salmon':(255,160,122),'orange red':(255,69,0),'dark orange':(255,140,0),'orange':(255,165,0),'gold':(255,215,0),'dark golden rod':(184,134,11),'golden rod':(218,165,32),'pale golden rod':(238,232,170),'dark khaki':(189,183,107),'khaki':(240,230,140),'olive':(128,128,0),'yellow':(255,255,0),'yellow green':(154,205,50),'dark olive green':(85,107,47),'olive drab':(107,142,35),'lawn green':(124,252,0),'chartreuse':(127,255,0),'green yellow':(173,255,47),'dark green':(0,100,0),'green':(0,128,0),'forest green':(34,139,34),'lime':(0,255,0),'lime green':(50,205,50),'light green':(144,238,144),'pale green':(152,251,152),'dark sea green':(143,188,143),'medium spring green':(0,250,154),'spring green':(0,255,127),'sea green':(46,139,87),'medium aqua marine':(102,205,170),'medium sea green':(60,179,113),'light sea green':(32,178,170),'dark slate gray':(47,79,79),'teal':(0,128,128),'dark cyan':(0,139,139),'aqua':(0,255,255),'cyan':(0,255,255),'light cyan':(224,255,255),'dark turquoise':(0,206,209),'turquoise':(64,224,208),'medium turquoise':(72,209,204),'pale turquoise':(175,238,238),'aqua marine':(127,255,212),'powder blue':(176,224,230),'cadet blue':(95,158,160),'steel blue':(70,130,180),'corn flower blue':(100,149,237),'deep sky blue':(0,191,255),'dodger blue':(30,144,255),'light blue':(173,216,230),'sky blue':(135,206,235),'light sky blue':(135,206,250),'midnight blue':(25,25,112),'navy':(0,0,128),'dark blue':(0,0,139),'medium blue':(0,0,205),'blue':(0,0,255),'royal blue':(65,105,225),'blue violet':(138,43,226),'indigo':(75,0,130),'dark slate blue':(72,61,139),'slate blue':(106,90,205),'medium slate blue':(123,104,238),'medium purple':(147,112,219),'dark magenta':(139,0,139),'dark violet':(148,0,211),'dark orchid':(153,50,204),'medium orchid':(186,85,211),'purple':(128,0,128),'thistle':(216,191,216),'plum':(221,160,221),'violet':(238,130,238),'magenta / fuchsia':(255,0,255),'orchid':(218,112,214),'medium violet red':(199,21,133),'pale violet red':(219,112,147),'deep pink':(255,20,147),'hot pink':(255,105,180),'light pink':(255,182,193),'pink':(255,192,203),'antique white':(250,235,215),'beige':(245,245,220),'bisque':(255,228,196),'blanched almond':(255,235,205),'wheat':(245,222,179),'corn silk':(255,248,220),'lemon chiffon':(255,250,205),'light golden rod yellow':(250,250,210),'light yellow':(255,255,224),'saddle brown':(139,69,19),'sienna':(160,82,45),'chocolate':(210,105,30),'peru':(205,133,63),'sandy brown':(244,164,96),'burly wood':(222,184,135),'tan':(210,180,140),'rosy brown':(188,143,143),'moccasin':(255,228,181),'navajo white':(255,222,173),'peach puff':(255,218,185),'misty rose':(255,228,225),'lavender blush':(255,240,245),'linen':(250,240,230),'old lace':(253,245,230),'papaya whip':(255,239,213),'sea shell':(255,245,238),'mint cream':(245,255,250),'slate gray':(112,128,144),'light slate gray':(119,136,153),'light steel blue':(176,196,222),'lavender':(230,230,250),'floral white':(255,250,240),'alice blue':(240,248,255),'ghost white':(248,248,255),'honeydew':(240,255,240),'ivory':(255,255,240),'azure':(240,255,255),'snow':(255,250,250),'black':(0,0,0),'dim gray / dim grey':(105,105,105),'gray / grey':(128,128,128),'dark gray / dark grey':(169,169,169),'silver':(192,192,192),'light gray / light grey':(211,211,211),'gainsboro':(220,220,220),'white smoke':(245,245,245),'white':(255,255,255)}
    list_of_colors = [[255,255,255],[254,223,203],[255,255,240],[253, 244, 220],[255,245,213],[255,255,205],[255,250,250],[248,248,255],[240,248,255],[250,250,210],[255,250,205],[250,235,215],[255,215,0],[205,133,63],[210,105,30],[244,164,96],[255,127,80],[255,117,24],[255,99,71],[204,71,75],[255,69,0],[255,192,203],[220,20,60],[139,0,0],[255,105,180],[200,5,134],[199,21,133],[138,43,226],[75,0,130],[135,206,250],[100,149,237],[5,102,245],[0,191,255],[240,255,255],[0,0,128],[175,238,238],[127,255,212],[64,224,208],[144,238,144],[0,255,0]]
    while(True):
        
        # print(dxcam.device_info())
        camera = dxcam.create()
        
        # print("imagegrab")
        # %timeit ImageGrab.grab() #Define an area to capture.
        # print("mss")
        # %timeit capture_screenshot()
        # print("pyautogui")
        # %timeit pyautogui.screenshot()

        image = ImageGrab.grab()
        buf = BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)
        print("extern lib")

        print("bincount")
        a = camera.grab()



        # %timeit buf = BytesIO()
        # buf = BytesIO()
        # %timeit image.save(buf, format='JPEG')
        # image.save(buf, format='JPEG')
        # buf.seek(0)
        # %timeit col_val = DominantColour(buf)
        # col_val = DominantColour(buf)
        
        
        # #bincount approach--------------------------------------------------
        # a = np.array(image)
        # #%timeit col_val = bincount_app(a)
        # col_val = bincount_app(a)
        # #col_val =bincount_app(a) 
        # %timeit color = [col_val[0], col_val[1], col_val[2]]
        # color = [col_val[0], col_val[1], col_val[2]]
        # #pillow approach
        # # img = image.resize((1, 1), resample=0)
        # # col_val = img.getpixel((0, 0))
        # # color = [col_val[0], col_val[1], col_val[2]]

        # #color = [col_val.r, col_val.g, col_val.b]
        # print("final color")
        # %timeit final_color = closest(list_of_colors, color)
        # final_color = closest(list_of_colors, color)
        # %timeit device.set_color(final_color)


# %%
async def main(email: str, password: str, ip_address: str):
    client = ApiClient(email, password)   
    device = await client.l530(ip_address)
    
    i = True
    while i:
        print('''Enter task:
        1. Toggle State
        2. Device Info
        3. Run Ambient Lighting
        4. Exit
        ''')
        task = input("Enter the number: ")
        print(task)
        
        if task == "1":
            print("Toggling bulb state...")
            await toggle_bulb(device)
        elif task == "2":
            print(device.get_device_info())
        elif task == "3":
            await gamer_mode(device)
        else:
            i = False

if __name__ == "__main__":
    email = os.getenv("API_EMAIL", "default@gmail.com")
    password = os.getenv("API_PASSWORD", "default_password")
    ip_address = os.getenv("DEVICE_IP", "192.168.1.000")
    asyncio.run(main(email, password, ip_address))

# %%



