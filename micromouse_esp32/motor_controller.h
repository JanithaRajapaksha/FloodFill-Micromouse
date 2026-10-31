#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include "navigator.h"

/**
 * Motor rotational direction for H-bridge drivers (DRV8833, TB6612, L298N, etc.).
 */
typedef enum {
    MOTOR_DIR_COAST = 0,
    MOTOR_DIR_FORWARD,
    MOTOR_DIR_REVERSE,
    MOTOR_DIR_BRAKE
} MotorDirection;

/**
 * Detailed actuation command for differential drive mobile robots.
 */
typedef struct {
    MotorDirection left_dir;
    MotorDirection right_dir;
    uint8_t left_pwm_percent;    // Speed from 0 to 100%
    uint8_t right_pwm_percent;   // Speed from 0 to 100%
    uint16_t move_distance_mm;   // Target linear travel (e.g. 180 mm standard cell pitch)
    int16_t turn_angle_deg;      // Target angular rotation: 0 (straight), +90 (right), -90 (left), 180 (turn around)
} MotorCommand;

/**
 * Configurable physical drive parameters.
 */
typedef struct {
    uint8_t drive_pwm;           // Base cruising duty cycle (e.g. 60%)
    uint8_t turn_pwm;            // Spin in place duty cycle (e.g. 40%)
    uint16_t cell_pitch_mm;      // Standard cell pitch (180 mm)
} MotorConfig;

/**
 * Hardware Abstraction Layer (HAL) callback hook.
 * The microcontroller firmware registers its platform-specific driver here
 * (e.g. setting GPIO direction pins and Timer PWM duty cycles).
 */
typedef void (*MotorHardwareDriverFn)(const MotorCommand *cmd, void *user_data);

/**
 * Abstract motor controller context.
 */
typedef struct {
    MotorConfig config;
    MotorHardwareDriverFn driver_hook;
    void *driver_user_data;
} MotorController;

/**
 * Initialize motor controller with configuration parameters.
 */
void motor_controller_init(MotorController *controller, const MotorConfig *config);

/**
 * Attach platform-specific motor driver callback hook.
 */
void motor_controller_set_driver(
    MotorController *controller,
    MotorHardwareDriverFn driver,
    void *user_data
);

/**
 * Translate a high-level NavCommand into an abstract MotorCommand.
 */
MotorCommand motor_controller_translate(
    const MotorController *controller,
    NavCommand nav_cmd
);

/**
 * Translate and dispatch to attached hardware driver if registered.
 */
MotorCommand motor_controller_execute(
    MotorController *controller,
    NavCommand nav_cmd
);

#endif /* MOTOR_CONTROLLER_H */

