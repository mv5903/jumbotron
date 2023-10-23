## Installation

## NOTE: If you are on Windows, you will probably need to install WSL2 and Ubuntu 20.04 LTS to run this project, or just run it on Mac or a Linux VM. You can follow the instructions here: https://docs.microsoft.com/en-us/windows/wsl/install-win10
You can probably do it in Windows, but all I've gotten are so many errors!

## Ok, here's how to install this project:

### Change directory
```cd backend```

### Create a virtual environment
```python3 -m venv venv```
Note: If this command fails saying that the Python virtual environment module is not installed, you can install it by running ```sudo apt install python3-venv``` on Ubuntu.

### Activate the virtual environment
```source venv/bin/activate```

### Install Flask
```pip3 install Flask```

### Exit from Python virtual environment
```deactivate```

### Change directory
```cd .. && cd frontend/led-matrix```

### Install dependencies
```npm install``` (if you get `permission denied`, try `sudo npm install` if on mac or linux)
You will have to run this again if `package.json` or `package-lock.json` gets modified to get the latest version of node dependencies. 

### Go back to root
```cd ..```

### Run Backend in one terminal:
```source backend/venv/bin/activate && python3 backend/api.py```

### Run Frontend in another terminal:
```cd frontend/led-matrix && npm run dev```, if you get `permission denied`, try `sudo npm run dev` instead in the previous command on mac or linux

### When finished you can stop them by pressing
```Ctrl+C``` in both terminals

### Exit from Python virtual environment, if you want to use this terminal window for something else
```deactivate```

## Testing

### Testing the API
You can simply navigate to ```http://localhost:5000/api/helloworld``` to test the API. You should see the following message:
```{"message":"Hello World!"}```

