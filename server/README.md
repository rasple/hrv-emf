# RF switching server

This Script starts a webserver and turns wireless (wifi & bluetooth) on and off when the right HTTP GET request is sent to the specified port.

`GET <HOST>:<PORT>/?action=<ACTION> HTTP/1.1`

`<ACTION>` can be either `on`, `off`, `toggle` or `status`

The user always receives information on the status of the wireless devices as response.

## Requirements
* GNU Core Utilities
* Python 3

Recommended:
* Python >= 3.7
* GNU/Linux Distro with systemd

## Installation

1. Place the script in any directory of your choice

    ```$ wget https://raw.githubusercontent.com/rasple/hrv-emf/master/server/switch_wireless_server.py```

2. Change to PORT variable in the script if you need one different from the default (31415)

3. Make it executable

    ```# chmod +x switch_wireless_server.py```

4. Start the script

    There are two ways the script can be run automatically. The first one is highly preferred.

    ### Systemd service (systemd distros)
    
    The file `rfswitch.service` is provided to be used to start the script as a systemd daemon.
        
    Place the script it in the `/etc/systemd/system/` directory
    
    Edit the `rfswitch.service` file to have the correct path to the `switch_wireless_server.py` script
     
    Reload the daemons to load the new service. Then enable and run it
        
        `# systemctl daemon-reload`
        
        `# systemctl enable rfswitch`
        
        `# systemctl start rfswitch`
       
     ### cronjob (any system)
     
     Use the package manager of your distro to install cronie if it isn't already
     
     `# pacman -S cronie`
     
     Enable the cron service
     
     `# systemctl enable cronie`

     Edit the crontab of your root user
     
     `# crontab -e`
     
     Add the following line and replace the placeholder with your path to the script. If you need logs, direct the output to your logfile. Consider however that there is no log rotation.
     
     `@reboot /<PATH_TO_THE_SCRIPT>/switch_wireless_server.py > /dev/null 2>&1`
     
     On the next reboot, the service should run. Verify with
     
     `$ ps aux | grep switch_wireless_server.py`
         
 ## Testing
 
 The functionality can be verified with `curl`. Keep in mind that RF is turned off when the script is first run.
 
 ```
$ curl 'http://<HOST>:31415/?action=toggle'
bluetooth unblocked
wlan unblocked
 ```
 
 ## TODO
 * Make a genuine python package that can be installed with `pip`