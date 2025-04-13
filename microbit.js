// ------------------ State Management ------------------
let state = "default"
let STATE_DEFAULT = "default"
let STATE_STOPWATCH_WAIT = "stopwatchWait"
let STATE_STOPWATCH_RUNNING = "stopwatchRunning"
let STATE_SHAKE = "shake"
let STATE_DATE = "date"
let DEVICE_NAME = control.deviceName()
let DATE = ""
let TIME = 0
let HEALTH_STAUS = 0 // 0: healthy, 1: unhealthy
let lastLight = 0
let lightSendInterval = 15000  // 30 seconds
let stopwatchStart = 0
let stateEnterTime = 0
let phrases = ["Keep going!", "You can do it!", "Believe!", "Yes you can!"]

// ------------------ Initialize Hardware ------------------
let _4digit = grove.createDisplay(DigitalPin.P2, DigitalPin.P16)
_4digit.point(true)
_4digit.clear()

// Initialize serial communication (via USB data cable)
// Map TX and RX to USB_TX and USB_RX, set baud rate to 115200
serial.redirect(SerialPin.USB_TX, SerialPin.USB_RX, BaudRate.BaudRate115200)

// ------------------ Helper Function ------------------
function enterState(newState: string) {
    state = newState
    stateEnterTime = control.millis()

    if (state == STATE_DEFAULT) {
        if (HEALTH_STAUS = 0) {
            basic.showIcon(IconNames.Happy)
        } else {
            basic.showIcon(IconNames.Sad)
        }
    } else if (state == STATE_STOPWATCH_WAIT) {
        basic.showIcon(IconNames.Asleep)
    } else if (state == STATE_STOPWATCH_RUNNING) {
        control.inBackground(function () {
            while (state == STATE_STOPWATCH_RUNNING) {
                basic.showIcon(IconNames.Asleep)
                basic.pause(500)
                basic.clearScreen()
                basic.pause(500)
            }
        })
    } else if (state == STATE_SHAKE) {
        let r = Math.randomRange(0, phrases.length - 1)
        basic.showString(phrases[r])
    } else if (state == STATE_DATE) {
        basic.showString(DATE)
    }
}

// ------------------ Serial Receive Handling ------------------
serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    let data = serial.readUntil(serial.delimiters(Delimiters.NewLine))
    // Handle time information
    if (data.substr(0, 2) == "T:") {
        let time = data.substr(2)
        let parts = time.split(":")
        if (parts.length == 2) {
            let h = parseInt(parts[0])
            let m = parseInt(parts[1])
            let hh = h < 10 ? "0" + h : "" + h
            let mm = m < 10 ? "0" + m : "" + m
            TIME = parseInt(hh + mm)
            _4digit.show(TIME)
            _4digit.point(true)
        }
    }
    // Handle date information
    else if (data.substr(0, 2) == "D:") {
        DATE = data.substr(2)
    }
    // Handle health status information
    else if (data.substr(0, 2) == "H:") {
        let healthStatus = data.substr(2).trim()
        // Update display only in default state
        if (healthStatus == "healthy") {
            HEALTH_STAUS = 0
        } else if (healthStatus == "unhealthy") {
            HEALTH_STAUS = 1
        }
    }
})


// ------------------ Serial Light Intensity Sender ------------------
control.inBackground(function () {
    while (true) {
        basic.pause(lightSendInterval)
        let currentLight = pins.analogReadPin(AnalogPin.P0)
        let diff = Math.abs(currentLight - lastLight)
        if (diff > 3) {
            let msg = "DID:" + DEVICE_NAME + ";" + "L:" + currentLight
            serial.writeLine(msg)
            lastLight = currentLight
        }
    }
})

// ------------------ State Timeout Check ------------------
basic.forever(function () {
    if (state == STATE_STOPWATCH_WAIT || state == STATE_SHAKE || state == STATE_DATE) {
        if (control.millis() - stateEnterTime > 10000) {
            enterState(STATE_DEFAULT)
        }
    }
})

// ------------------ Button A Controls Stopwatch ------------------
input.onButtonPressed(Button.A, function () {
    if (state == STATE_STOPWATCH_RUNNING) {
        let elapsed = (control.millis() - stopwatchStart) / 1000
        let rounded = Math.round(elapsed * 10) / 10
        basic.showString(rounded + "s")
        enterState(STATE_DEFAULT)
        return
    }
    if (state == STATE_DEFAULT) {
        enterState(STATE_STOPWATCH_WAIT)
        return
    }
    if (state == STATE_STOPWATCH_WAIT) {
        stopwatchStart = control.millis()
        enterState(STATE_STOPWATCH_RUNNING)
        return
    }
    if (state == STATE_DATE || state == STATE_SHAKE) {
        enterState(STATE_DEFAULT)
        return
    }
})

// ------------------ Button B Controls Date Display ------------------
input.onButtonPressed(Button.B, function () {
    if (state == STATE_STOPWATCH_RUNNING) {
        return
    }
    if (state == STATE_DEFAULT) {
        enterState(STATE_DATE)
        return
    }
    enterState(STATE_DEFAULT)
})

// ------------------ Shake Gesture Event ------------------
input.onGesture(Gesture.Shake, function () {
    if (state == STATE_STOPWATCH_RUNNING) {
        return
    }
    if (state == STATE_DEFAULT) {
        enterState(STATE_SHAKE)
    }
})

// ------------------ Start with Default State ------------------
enterState(STATE_DEFAULT)
