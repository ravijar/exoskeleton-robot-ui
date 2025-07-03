#include <Wire.h>
#include <MPU6050_6Axis_MotionApps20.h>
#include <QMC5883LCompass.h>

MPU6050 mpu;
QMC5883LCompass compass;

bool dmpReady = false;
uint8_t fifoBuffer[64];
Quaternion q;
VectorFloat gravity;
float ypr[3];

// Calibration for magnetometer
int magMinX = -1530, magMaxX = 917;
int magMinY = -1268, magMaxY = 1120;
int magMinZ = -240,  magMaxZ = 727;

// Kalman pitch filter variables
float pitchKF, biasPitch, ratePitch;
float P_pitch[2][2] = {{1, 0}, {0, 1}};
float Q_angle_pitch = 0.001, Q_bias_pitch = 0.003, R_measure_pitch = 0.03;

// Compass smoothing
float avgMx = 0, avgMy = 0, avgMz = 0;
float COMPASS_ALPHA = 0.2;
float alpha = 0.05;  // roll filter

float filterRoll = 0;
float fusedYaw = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  mpu.initialize();
  mpu.setXAccelOffset(-1116);
  mpu.setYAccelOffset(-608);
  mpu.setZAccelOffset(148);
  mpu.setXGyroOffset(-18);
  mpu.setYGyroOffset(10);
  mpu.setZGyroOffset(74);

  if (mpu.dmpInitialize() == 0) {
    mpu.setDMPEnabled(true);
    dmpReady = true;
    Serial.println("MPU6050 DMP Ready!");
  } else {
    Serial.println("DMP init failed.");
  }

  compass.init();
  Serial.println("Compass Initialized!");
}

void loop() {
  if (!dmpReady) return;
  float dt = 0.02;  // fixed time step (50Hz)

  if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
    mpu.dmpGetQuaternion(&q, fifoBuffer);
    mpu.dmpGetGravity(&gravity, &q);
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);

    // Raw YPR
    float rawPitch = ypr[1] * 180.0 / PI;
    float rawRoll  = ypr[2] * 180.0 / PI;
    float rawYaw   = ypr[0] * 180.0 / PI;
    if (rawPitch > 180) rawPitch -= 360;
    if (rawPitch < -180) rawPitch += 360;
    if (rawYaw > 180) rawYaw -= 360;
    if (rawYaw < -180) rawYaw += 360;

    float gyroY = mpu.getRotationY() / 131.0;  // °/s
    float gyroZ = mpu.getRotationZ() / 131.0;  // °/s

    // Kalman filtered pitch
    float rate = gyroY - biasPitch;
    pitchKF += dt * rate;
    P_pitch[0][0] += dt * (dt * P_pitch[1][1] - P_pitch[0][1] - P_pitch[1][0] + Q_angle_pitch);
    P_pitch[0][1] -= dt * P_pitch[1][1];
    P_pitch[1][0] -= dt * P_pitch[1][1];
    P_pitch[1][1] += Q_bias_pitch * dt;
    float S = P_pitch[0][0] + R_measure_pitch;
    float K[2] = {P_pitch[0][0] / S, P_pitch[1][0] / S};
    float y = rawPitch - pitchKF;
    pitchKF += K[0] * y;
    biasPitch += K[1] * y;
    P_pitch[0][0] -= K[0] * P_pitch[0][0];
    P_pitch[0][1] -= K[0] * P_pitch[0][1];
    P_pitch[1][0] -= K[1] * P_pitch[0][0];
    P_pitch[1][1] -= K[1] * P_pitch[0][1];

    // Smoothed roll
    filterRoll = alpha * rawRoll + (1 - alpha) * filterRoll;

    // Read and smooth magnetometer
    compass.read();
    avgMx = COMPASS_ALPHA * compass.getX() + (1 - COMPASS_ALPHA) * avgMx;
    avgMy = COMPASS_ALPHA * compass.getY() + (1 - COMPASS_ALPHA) * avgMy;
    avgMz = COMPASS_ALPHA * compass.getZ() + (1 - COMPASS_ALPHA) * avgMz;

    float offsetX = (magMaxX + magMinX) / 2.0;
    float offsetY = (magMaxY + magMinY) / 2.0;
    float offsetZ = (magMaxZ + magMinZ) / 2.0;

    float scaleX = 2.0 / (magMaxX - magMinX);
    float scaleY = 2.0 / (magMaxY - magMinY);
    float scaleZ = 2.0 / (magMaxZ - magMinZ);

    float normX = (avgMx - offsetX) * scaleX;
    float normY = (avgMy - offsetY) * scaleY;
    float normZ = (avgMz - offsetZ) * scaleZ;

    float pitch = pitchKF * DEG_TO_RAD;
    float roll  = filterRoll * DEG_TO_RAD;

    // Tilt compensation
    float magXh = normX * cos(pitch) + normZ * sin(pitch);
    float magYh = normX * sin(roll) * sin(pitch) + normY * cos(roll) - normZ * sin(roll) * cos(pitch);
    float tiltYaw = atan2(magYh, magXh) * 180.0 / PI;

    if (tiltYaw > 180) tiltYaw -= 360;
    if (tiltYaw < -180) tiltYaw += 360;

    // Complementary yaw filter
    fusedYaw = 0.98 * (fusedYaw + gyroZ * dt) + 0.02 * tiltYaw;

    // Print final values
    Serial.print("Yaw: ");
    Serial.print(fusedYaw, 1);
    Serial.print("  Pitch: ");
    Serial.println(pitchKF, 1);

    delay(20);  // 50 Hz update
  }
}