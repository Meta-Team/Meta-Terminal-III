# Meta-Terminal III

> This is the source code for the Meta-Terminal III. The Meta-Terminal III is a tool that helps the Meta Team adjust parameters with configurable interface. This tool is written in python with the modules from PyQT5.

You can run the tool from the source code by typing

```shell
python3 main.py
```

in your computer terminal under the same directory.

## Use of configuration file

The configuration file helps you define your testing interface. There are some presevered keywords and you can define your own parameters and commands so long as you follow the rules. The configuration file must be consisted with the test code and you should double check before running testing.

### Preserved keywords and commands

+ **project**: The name of the test, not important.
+ **motor_config**: A list of configurations for each motor.
+ **motor_id**: The id of the motor. The number will be fit into the command indicating the motor to which the command is sent. id should be unique and consistant with your code.
+ **motor_name**: The name for the motor, marking the motor in the interface.
+ **commands**: Put any other commands that you will need in your testing here. If the name of the parameter is not in the preserved keywords, it will be automatically recognized as a self-defined keyword. If the command may be used for each motor seperately, set the first parameter to be **"motor_id"**. If the command is only for one or more but not all motors, list the motors' names in the command and put a **"->"** before the names start. If there is neither **"motor_id"** in the first place nor **"->"**, the command will be considered a global command.

### Format of feedback

For the convenience of graphic displacement, the feedback should follow some patterns:

+ For the **graphic displaceable** message, the feedback should follow the pattern of **"fb \[motor_name] \[angle] \[target_angle] \[velocity] \[target_velocity] \[current] \[target_current]"** (replace the value in "[]" with real value). One example could be "fb yaw 356.7 360.0 3.7 4.0 1274.32 1000.00". Make sure each feedback message has **6 numerical parameters**, fill the ones with 0 if you have no value for it. The **\[motor_name]** should be consistant with the **motor_name** in your configuration file.
+ For the **pure textual** message, please avoid starting with "fb".

An example of configuration file and test file can be seen in the example folder.