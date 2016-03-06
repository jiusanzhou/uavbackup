## MAVinline

* Control by MAVProxy


### TODO

* <del>Arm the aircraft
  * `arm throttle`
* waypoint
* keep distance
* Control direction
* Control senvos beyond flying senvos
* Measure distance and process the data returns from opencv

---

* Finish the udp server witch can store the sended data and


### All commands

* accelcal             : do 3D accelerometer calibration
* ahrstrim             : do AHRS trim
* alias                : command aliases
* alt                  : show altitude information
* arm                  : arm motors
* auxopt               : select option for aux switches on CH7 and CH8 (ArduCopter only)
* bat                  : show battery information
* calpress             : calibrate pressure sensors
* camctrlmsg           : camctrlmsg
* cammsg               : cammsg
* changealt            : change target altitude
* compassmot           : do compass/motor interference calibration
* disarm               : disarm motors
* fence                : geo-fence management
* ground               : do a ground start
* guided               : fly to a clicked location on map
* gyrocal              : do gyro calibration
* land                 : auto land
* level                : set level on a multicopter
* link                 : link control
* log                  : log file handling
* magcal               : magcal
* mode                 : mode change
* module               : module commands
* motortest            : motortest commands
* output               : output control
* param                : parameter handling
* rally                : rally point control
* rc                   : RC input control
  * This commend modify the value of rc stack. We can control the copter with computer without rc controler.
* rcbind               : bind RC receiver
* reboot               : reboot autopilot
  * Reboot the aircraft, NEVER USE IT WHILE FLYING.
* relay                : relay commands
* repeat               : repeat a command at regular intervals
* reset                : reopen the connection to the MAVLink master
  * Reconnect the master
* script               : run a script of MAVProxy commands
  * Run commends in a file
* servo                : servo commands
  * Control the servos (5 to 8)
  * Format, `servo set NO. PWM`
  * 1 to 4 is for flying servos
  * PWM value in the range of 1100 to 1950
* set                  : mavproxy settings
* setspeed             : do_change_speed
  * Change the velocity
* setup                : go into setup mode
  * Error in terminal
* setyaw               : condition_yaw
  * Set the yaw's condition?
* shell                : run shell command
* status               : show status
  * Write the status to a file or stdout.
* switch               : flight mode switch control
  * Change the flight mode
  * `switch NO.`
  * Also can type `mode MODENAME`
* takeoff              : takeoff
  * Takeoff, never try
  * `takeoff contance`
* terrain              : terrain control
* time                 : show autopilot time
* tuneopt              : Select option for Tune Pot on Channel 6 (quadcopter only)
  * Adjust something on Channel 6
* up                   : adjust pitch trim by up to 5 degrees
  * Adjust pitch trim
* velocity             : velocity
* version              : show version
* watch                : watch a MAVLink pattern
* wp                   : waypoint management
  * Waypoint.

### Status

> The data returns from `status` commend is comes from `mpstate.status.msgs`.

They are:
* `VFR_HUD`
* `ATTITUDE`
* `HEARTBEAT`
* `MISSION_CURRENT`
* `RAW_IMU`
* `GPS_RAW_INT`
* `SCALED_IMU2`
* `NAV_CONTROLLER_OUTPUT`
* `VFR_HUD`
* `MEMINFO`
* `HWSTATUS`
* `STATUSTEXT`
* `BAD_DATA`
* `SENSOR_OFFSETS`
* `AHRS`
* `SCALED_PRESSURE`
* `GLOBAL_POSITION_INT`,
* `SYS_STATUS`,
* `POWER_STATUS`
* `PARAM_VALUE`
* `SYSTEM_TIME`
* `SERVO_OUTPUT_RAW`
* `RC_CHANNELS_RAW`

Maybe more...

### RC

> Using `RC` commend is a way to control the copter. The channel value is 1100 ~ 1950(RC1~RC8), get the current values by `status RC_CHANNELS_RAW`

* channel 1: left-right
* channel 2: front-rear
* channel 3: up-down
* channel 4: yaw_left-yaw_right
* channel 5: -
* channel 6: manual_control
* channel 7: -
* channel 8: -

### Software flow

#### How Important GPS!

**NOT BE IMPORTANT MORE!**

* The `loiter` is depended on GPS data
* All the control below logic is depended on `loiter` mode
* Hence closer to the building, gps data LESS!
* Any solution to fix this?

#### What Should I Do?

1. Update the status
2. Send the status to UDP server and get commands back
3. Process commands which back from server(NOT IMMEDIATE)
4. Get mpstates's status from sensor like sonars and camera, and save them
5. Process the mpstates's status to make some actions
6. Process commands to justfy the mpstate who to do work(IMMEDIATE)

#### How Shold I Do?


1. Main thread

  * Update the status of mpstate.  
    - Distance of four/six dorection.(Module `signal` can not work in the subprocess)
    - NO FOR INPUT ANYMORE

2. Update stauts thread

  * Get the aitcraft's status saved to status.

3. Send UDP heart thread

  * Send the mpstate's status to server, and get commands data back.
    - Put commands into QUEUE.

  * This thread will sleep for X second to adjust vericity of sendding UDP data.
    - This is not a good way to do this, but now no idea.


#### What should be saved?

1. GPS data
  * 0 means lost GPS starts
  * Auto model can only active with GPS ready.(Count of stars is enough)
2. Armded
3. Heigh or takeoff finished.
4. Four directions' distance.
5. Clean work started or not.
6. Mode of aircraft.

#### What can users do?

* Choose a point on the map
* Choose a aircraft on the area
* Set the flight way(Measure distance, if fine, send the data to server)
* Arm aircraft
* Takeoff(With heigh, or auto takeoff)
* Cancel this mission(Aircraft will return the launched points)
* Disarm aircraft

#### Waht can users see?

* Aircraft on map and the status
* The area that aircraft can reach
* Choosed way line
* Work started or not
* The picture
* Home point