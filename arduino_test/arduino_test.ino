#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX

void setup() {
    // Open serial communications and wait for port to open:
    Serial.begin(115200);
    while (!Serial) {
        ; // wait for serial port to connect. Needed for native USB port only
    }


    Serial.println("Goodnight moon!");

    // set the data rate for the SoftwareSerial port
    mySerial.begin(115200);
    mySerial.println("Hello, world?");
}

// void loop() { // run over and over
//   if (mySerial.available()) {
//     Serial.write(mySerial.read());
//   }
//   if (Serial.available()) {
//     mySerial.write(Serial.read());
//   }
// }

bool feedback_enable = false;
String received_data = "";
unsigned char iter_time = 0;
int angle_1, velocity_1, current_1;
int target_angle_1, target_velocity_1, target_current_1;
int angle_2, velocity_2, current_2;
int target_angle_2, target_velocity_2, target_current_2;
char motor_1[] = "yaw";
char motor_2[] = "pitch";
char send_data[500];

void loop() { // run over and over
    while (Serial.available() > 0){
        received_data += char(Serial.read());
    }
    if (received_data == "fb 1\n"){
        feedback_enable = true;
    } else if (received_data == "fb 0\n"){
        feedback_enable = false;
    }
    if (feedback_enable){
        angle_1 = (int)(128 * sin(PI * iter_time / 128));
        target_angle_1 = (int)(128 * cos(PI * iter_time / 128));
        velocity_1 = (int)(128 * ((char)iter_time - 128) / 128.0f);
        target_velocity_1 = -(int)(128 * ((char)iter_time - 128) / 128.0f);
        current_1 = (int)(128 * exp(iter_time / 256.0) - 1);
        target_current_1 = (int)(128 * (1 - exp(iter_time / 256.0)));
        angle_2 = (int)(128 * ((char)iter_time - 128) / 128.0f);
        target_angle_2 = -(int)(128 * ((char)iter_time - 128) / 128.0f);
        velocity_2 = (int)(128 * (exp(iter_time / 256.0) - 1));
        target_velocity_2 = (int)(128 * (1 - exp(iter_time / 256.0)));
        current_2 = (int)(128 * sin(PI * iter_time / 128));
        target_current_2 = (int)(128 * cos(PI * iter_time / 128));
        
        sprintf(send_data, "fb %s %d %d %d %d %d %d\nfb %s %d %d %d %d %d %d", motor_1, angle_1, target_angle_1, velocity_1, target_velocity_1, current_1, target_current_1, 
                                                                               motor_2, angle_2, target_angle_2, velocity_2, target_velocity_2, current_2, target_current_2);
        Serial.println(send_data);
        iter_time += 1;
        // Serial.println("Hello from Hardware Serial!");
        // mySerial.println("Hello from Software Serial!");
    }
    received_data = "";
    delay(10);
}
