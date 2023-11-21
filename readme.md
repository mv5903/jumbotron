## Jumbotron!
<img src="./images/demo.JPG" width="400" style="text-align: center" />
<br><br>

### The backstory

I always loved tinkering with Raspberry Pis and other IoT devices. I really got into [Home Assistant](https://www.home-assistant.io/) in the last year, and I now have a great smart home (room as I'm still in college). I have a ton of smart lights, and have [Proxmox](https://www.proxmox.com/en/) running a lot of LXC containers. I have had Raspberry Pis for a good several years now, and have done all the basic things like running a [PiHole](https://pi-hole.net/) (which I now use my Proxmox server for), a web server (now through Firebase), and a few other things. I have always wanted to do something with a Raspberry Pi that was more than just a simple project, as those 40 hardware pins that come with it are capable of more than just a typical computer. I wanted to do something that would be fun, and that I could use for a long time. Ultimately, I went with this LED matrix which I like to call a Jumbotron. I love the way addressable RGBs look with all the patterns and specificity there is with them.

### Intended Purpose

I want this matrix to be something that can be capable of nearly anything I throw at it. I could display images, and videos, and have people text in stuff; the possibilities are endless. I want to be able to use this for events, parties, and just for fun. I want to be able to use this for my own personal use, but also for others to use as well. Whatever it may be, I want this to be a fun project that I can use to learn more about Raspberry Pi hardware, Python, and the world of IoT. 

### How it works

#### The Software

You see most of it in this Repo, but to give a general overview:
- Backend: Python Flask API with Socket.io
- Frontend: Vite React.js with Typescript

The `api.py` file is registered as a systemd service and runs at startup; it is always running when the Raspberry Pi is.

Also, the brightness goes from `0-255` but when I put on the full brightness in a well-lit room it nearly burns my eyeballs out. So I typically will set the maximum to `40` as the maximum as it is plenty bright and prevents visible voltage drop, which improves color accuracy. Plus, this is mainly something that would be shown during the nighttime anyway. 

#### The Hardware

I'm working on a wiring diagram, but for now, here's a general overview:
- Raspberry Pi 4 4GB (you don't really need this much power but this is just what I happened to have lying around)
- 11x [BTF-Lighting WS218B Addressable RGB LED Strips](https://www.amazon.com/gp/product/B01CDTEKAG/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1), which with trimming gives my full 64 x 48 matrix (3072 LEDs)
- 4x [BTF-Lighting 5V 60A Power Supplies](https://www.amazon.com/gp/product/B01D8FLZV6/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1) (I will never come close to using this much power, but I wanted to be on the safe end and have that power available just in case)
- Jumper wires
- [SunFounder RAB Holder Breadboard Kit](https://www.amazon.com/gp/product/B07ZYR7R8X/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1) (I ended up ditching the breakout board because it was very flimsy and I instead opted for male-to-female jumper wires to connect the Pi pins I needed directly to the breadboard)
- 22 AWG gauge wire (same type that comes with the LED strips; for connecting them together)
- 16 AWG gauge wire (for power in groups of 3)
- 4x Multipurpose power cords with ground (for power supplies)
- Huge piece of plywood (for mounting the LED strips), decide this based on your LED density and how big you want your matrix to be
- Wire crimps
- Wire strippers
- Wire cutters
- Soldering iron
- Solder
- Something to clean the soldering iron tip with
- Hot glue gun or super glue (for mounting the LED strips to the plywood more permanently than the included 2-sided tape)
- *[Not Required]* [Small OLED display](https://www.amazon.com/gp/product/B09T6SJBV5/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) (for displaying the IP address of the Pi and showing the current CPU and memory usage)
- *[Not Required]* Power meter (for measuring the power draw of the jumbotron system, which will  include the Raspberry Pi as well)

Probably some other minor things I am missing but this should be the majority of it.

### How to wire

The Raspberry Pi has many GPIO ports, but depending on how long your strip is could make a difference in your choice of pins. I personally chose pin `GPIO21` because it supports full PCM and because it supports over 5400 LEDs! PVM is another option, which is shared by two other GPIO pins, but the disadvantage to this is the limit is 2700 LEDs, which is less than my desired 3072. There seems to be very little latency as well, so it fits my needs best.

To wire it all up, I placed strips cut off 64, and alternated the wiring. I started the 64 lights of a strip and placed them in an alternating pattern starting from the bottom. This seems to also be the sweet spot in terms of power-to-voltage drop color accuracy issues. The data, however, can continue all the way until the last strip. In this case, I only needed to connect 4 strips together with each end of their `GND` and `+5V` contact points, but as I said previously, data or `DIN`/`DOUT` can continue all the way until the last strip.

I connected `GPIO21` directly to the first strip's `DIN` solder point. In groups of 3 leads (4 total) since there are 12 groups of 4, I sent them down to their each dedicated 5V60A power supply `(+)` and `(-)` screws. On each of the powers supplies, the `(-)`'s are bridged directly to each other between supplies. From the power supply, I connected the `(-)` to one of the `GND` pins on the Raspberry Pi so that it shares a common ground with the LED strips. This step is really important and doesn't seem like it matters, but it will cause your LEDs to light up random colors and corrupt the colors of the LEDs. 

All five devices are then connected to a surge-protected power strip, then it is connected to the power metering device so that I can measure the power draw of the system.

## Thanks for reading! If you have any questions, feel free to contact me via my website, [mattvandenberg.com](http://www.mattvandenberg.com)!



