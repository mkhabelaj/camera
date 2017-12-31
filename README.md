# Motion Detection Camera

The Idea behind this module is to create a motion detection camera

##Requirements

1. Openvc
1. numpy
1. imutils


## Usage
1. Setup a virtual enviroment using python [Here is the documentation](http://virtualenvwrapper.readthedocs.io/en/latest/install.html)
1. Install Openvc [this is the guide I followed](https://www.learnopencv.com/install-opencv3-on-ubuntu)
   1. Tip ensure numpy is install in your python site or dist-packages
1. create a config file for the camera object ie
   1. ` 
   conf = {
    "show_video": True,
    "use_dropbox": True,
    "dropbox_access_token": "YOUR_DROPBOX_KEY",
    "dropbox_base_path": "YOUR_DROPBOX_PATH",
    "min_upload_seconds": 3.0,
    "min_motion_frames": 8,
    "camera_warmup_time": 2.5,
    "delta_thresh": 5,
    "resolution": [640, 480],
    "fps": 16,
    "min_area": 5000} 
    `
1. create the camera object and initialise()
   1. c = Camera(0,**conf)
   1. c.initialise_camera()
   

