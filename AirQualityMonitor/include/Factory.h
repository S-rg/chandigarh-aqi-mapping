/**
 * @file
 * @brief Factory to create all the sensors
 *
 * Create all the sensor objects and transfer ownership to manager.
 *
 * @details [Optional: Add more detailed information about the file, such as its
 * structure, dependencies, or any specific implementation details.]
 */

#include "SensorsConfig.h"
#include "Base.h"
#include "Sensors.h"

class SensorFactory {
private:
    /**
     * @brief Assigns the right Serial Stream / TwoWire object from a given config
     * @param sensor_cfg 
     * @return sensor_comms_ptr
     */
    CommsInterface* assignCommPtr(SensorInfo* sensor_cfg) {

        CommsInterface* sensor_comm = nullptr;

        if (sensor_cfg->comms == COMM_HARDWARE_SERIAL) {
            switch (sensor_cfg->port_no) {
                case 1:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial1);
                    break;
                case 2:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial2);
                    break;
                case 3:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial3);
                    break;
                case 4:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial4);
                    break;
                case 5:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial5);
                    break;
                case 6:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial6);
                    break; 
                case 7:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial7);
                    break; 
                case 8:
                    sensor_comm = new SerialInterface(sensor_cfg, Serial8);
                    break;  
                default:
                    sensor_comm = nullptr;
                    break;
            }
        }

        else if (sensor_cfg->comms == COMM_SOFTWARE_SERIAL) {
            // Needs to be a pointer so this object is not deleted once this conditional block is executed.ß
            SoftwareSerial* commObject = new SoftwareSerial(sensor_cfg->rx_pin, sensor_cfg->tx_pin);
            sensor_comm = new SerialInterface(sensor_cfg, *commObject);
        }

        else if (sensor_cfg->comms == COMM_I2C) {
            switch (sensor_cfg->port_no) {
                case 0:
                    sensor_comm = new I2CInterface(sensor_cfg, Wire);
                    break;
                case 1:
                    sensor_comm = new I2CInterface(sensor_cfg, Wire1);
                    break;
                case 2:
                    sensor_comm = new I2CInterface(sensor_cfg, Wire2);
                    break;
                default:
                    sensor_comm = nullptr;
                    break;
            }
        }

        if (sensor_comm == nullptr) {
            Serial.printf("[FATAL] Comm ptr not assigned for SensorID %i\n", sensor_cfg->sensor_id);
        }
        return sensor_comm;
    }
    


public: 
    SensorBase* createSensor(SensorInfo* sensor_cfg) {
        if (std::string(sensor_cfg->type) == "TVOCSensor") {
            return new TVOCSensor(sensor_cfg, assignCommPtr(sensor_cfg));
        }
        if (std::string(sensor_cfg->type) == "PMS7003Sensor") {
            return new PMS7003Sensor(sensor_cfg, assignCommPtr(sensor_cfg));
        }
        if (std::string(sensor_cfg->type) == "CH2OSensor") {
            return new CH2OSensor(sensor_cfg, assignCommPtr(sensor_cfg));
        }
        if (std::string(sensor_cfg->type) == "DFRobotOxygenSensor") {
            return new DFRobotOxygenSensor(sensor_cfg, assignCommPtr(sensor_cfg));
        }
        if (std::string(sensor_cfg->type) == "SO2Sensor") {
            return new SO2Sensor(sensor_cfg, assignCommPtr(sensor_cfg));
        }
        if (std::string(sensor_cfg->type) == "DFRobotCOSensor") {
            return new DFRobotCOSensor(sensor_cfg, assignCommPtr(sensor_cfg));
        }
        return nullptr;
    }
};
