/*
 * 二轴云台控制器 - ESP32代码
 * 使用 ESP32Servo 库控制舵机
 * 
 * 安装库: 在Arduino IDE中搜索 "ESP32Servo" 并安装
 * 
 * 连接说明:
 *   水平舵机(pan) -> GPIO 2
 *   垂直舵机(tilt) -> GPIO 4
 *   舵机电源 -> 5V
 *   GND -> GND
 */

#include <ESP32Servo.h>

// 舵机引脚定义
#define PAN_SERVO_PIN  2   // 水平舵机引脚
#define TILT_SERVO_PIN 4   // 垂直舵机引脚

// 舵机对象
Servo panServo;
Servo tiltServo;

// 当前角度
int panAngle = 90;
int tiltAngle = 90;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // 附加舵机到引脚
  panServo.attach(PAN_SERVO_PIN);
  tiltServo.attach(TILT_SERVO_PIN);
  
  // 设置初始位置
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
  
  Serial.println("Gimbal Ready");
}

void loop() {
  // 处理串口命令
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
}

void processCommand(String cmd) {
  if (cmd.length() < 2) return;
  
  char type = cmd.charAt(0);
  int value = cmd.substring(1).toInt();
  
  // 限制角度范围
  value = constrain(value, 0, 180);
  
  switch (type) {
    case 'P':
    case 'p':
      panAngle = value;
      panServo.write(panAngle);
      Serial.print("Pan: ");
      Serial.println(panAngle);
      break;
      
    case 'T':
    case 't':
      tiltAngle = value;
      tiltServo.write(tiltAngle);
      Serial.print("Tilt: ");
      Serial.println(tiltAngle);
      break;
      
    case 'R':
    case 'r':
      panAngle = 90;
      tiltAngle = 90;
      panServo.write(panAngle);
      tiltServo.write(tiltAngle);
      Serial.println("Reset");
      break;
  }
}