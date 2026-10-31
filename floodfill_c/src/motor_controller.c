#include <stddef.h>
#include "motor_controller.h"

static const MotorConfig DEFAULT_CONFIG = {
    .drive_pwm = 60,
    .turn_pwm = 40,
    .cell_pitch_mm = 180
};

void motor_controller_init(MotorController *controller, const MotorConfig *config) {
    if (!controller) return;

    if (config) {
        controller->config = *config;
    } else {
        controller->config = DEFAULT_CONFIG;
    }
    controller->driver_hook = NULL;
    controller->driver_user_data = NULL;
}

void motor_controller_set_driver(
    MotorController *controller,
    MotorHardwareDriverFn driver,
    void *user_data
) {
    if (!controller) return;
    controller->driver_hook = driver;
    controller->driver_user_data = user_data;
}

MotorCommand motor_controller_translate(
    const MotorController *controller,
    NavCommand nav_cmd
) {
    MotorCommand cmd = {
        .left_dir = MOTOR_DIR_BRAKE,
        .right_dir = MOTOR_DIR_BRAKE,
        .left_pwm_percent = 0,
        .right_pwm_percent = 0,
        .move_distance_mm = 0,
        .turn_angle_deg = 0
    };

    const MotorConfig *cfg = controller ? &controller->config : &DEFAULT_CONFIG;

    switch (nav_cmd) {
        case NAV_CMD_MOVE_FORWARD:
            cmd.left_dir = MOTOR_DIR_FORWARD;
            cmd.right_dir = MOTOR_DIR_FORWARD;
            cmd.left_pwm_percent = cfg->drive_pwm;
            cmd.right_pwm_percent = cfg->drive_pwm;
            cmd.move_distance_mm = cfg->cell_pitch_mm;
            cmd.turn_angle_deg = 0;
            break;

        case NAV_CMD_TURN_LEFT:
            // Pivot counter-clockwise (-90 deg) and advance
            cmd.left_dir = MOTOR_DIR_REVERSE;
            cmd.right_dir = MOTOR_DIR_FORWARD;
            cmd.left_pwm_percent = cfg->turn_pwm;
            cmd.right_pwm_percent = cfg->turn_pwm;
            cmd.move_distance_mm = cfg->cell_pitch_mm;
            cmd.turn_angle_deg = -90;
            break;

        case NAV_CMD_TURN_RIGHT:
            // Pivot clockwise (+90 deg) and advance
            cmd.left_dir = MOTOR_DIR_FORWARD;
            cmd.right_dir = MOTOR_DIR_REVERSE;
            cmd.left_pwm_percent = cfg->turn_pwm;
            cmd.right_pwm_percent = cfg->turn_pwm;
            cmd.move_distance_mm = cfg->cell_pitch_mm;
            cmd.turn_angle_deg = 90;
            break;

        case NAV_CMD_TURN_AROUND:
            // Spin 180 deg and advance
            cmd.left_dir = MOTOR_DIR_REVERSE;
            cmd.right_dir = MOTOR_DIR_FORWARD;
            cmd.left_pwm_percent = cfg->turn_pwm;
            cmd.right_pwm_percent = cfg->turn_pwm;
            cmd.move_distance_mm = cfg->cell_pitch_mm;
            cmd.turn_angle_deg = 180;
            break;

        case NAV_CMD_STOP:
        default:
            cmd.left_dir = MOTOR_DIR_BRAKE;
            cmd.right_dir = MOTOR_DIR_BRAKE;
            cmd.left_pwm_percent = 0;
            cmd.right_pwm_percent = 0;
            cmd.move_distance_mm = 0;
            cmd.turn_angle_deg = 0;
            break;
    }

    return cmd;
}

MotorCommand motor_controller_execute(
    MotorController *controller,
    NavCommand nav_cmd
) {
    MotorCommand cmd = motor_controller_translate(controller, nav_cmd);

    if (controller && controller->driver_hook) {
        controller->driver_hook(&cmd, controller->driver_user_data);
    }

    return cmd;
}
