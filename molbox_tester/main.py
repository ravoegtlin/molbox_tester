#!/usr/bin/env python3
"""
Main module for molbox_tester.

Connects to a host via telnet, sends commands periodically, and logs responses.
Implements timeout handling and automatic reconnection.
"""

import telnetlib
import time
import logging
import sys
import os
from pathlib import Path
from configparser import ConfigParser


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MolboxTester:
    """Telnet client for periodic command execution with timeout handling."""

    def __init__(self, host, port, interval, command, timeout=10):
        """
        Initialize MolboxTester.

        Args:
            host (str): Host address to connect to
            port (int): Port number
            interval (float): Interval in seconds between commands
            command (str): Command to send
            timeout (int): Timeout in seconds for receiving response
        """
        self.host = host
        self.port = port
        self.interval = interval
        self.command = command
        self.timeout = timeout
        self.tn = None

    def connect(self):
        """Establish telnet connection to the host."""
        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=self.timeout)
            logger.info("Connected successfully")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Close the telnet connection."""
        if self.tn:
            try:
                self.tn.close()
                logger.info("Disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.tn = None

    def send_command(self):
        """
        Send command and read response.

        Returns:
            bool: True if successful, False if timeout or error occurred
        """
        try:
            # Send command
            command_bytes = (self.command + "\r\n").encode('ascii')
            self.tn.write(command_bytes)
            logger.info(f"Sent: {self.command}")

            # Read response with timeout
            response = self.tn.read_until(b"\n", timeout=self.timeout)
            
            if response:
                response_str = response.decode('ascii', errors='ignore').strip()
                logger.info(f"Received: {response_str}")
                return True
            else:
                logger.warning("No response received within timeout")
                return False

        except EOFError:
            logger.error("Connection closed by remote host")
            return False
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False

    def run(self):
        """Main loop: send commands periodically with reconnection logic."""
        logger.info("Starting molbox_tester...")
        logger.info(f"Configuration: host={self.host}, port={self.port}, "
                   f"interval={self.interval}s, command={self.command}, timeout={self.timeout}s")

        while True:
            # Ensure we're connected
            if not self.tn:
                if not self.connect():
                    logger.warning(f"Retrying connection in {self.interval} seconds...")
                    time.sleep(self.interval)
                    continue

            # Send command and handle response
            success = self.send_command()
            
            if not success:
                # Timeout or error occurred, reconnect
                logger.warning("Reconnecting due to timeout or error...")
                self.disconnect()
                if not self.connect():
                    logger.warning(f"Reconnection failed, retrying in {self.interval} seconds...")
                    time.sleep(self.interval)
                    continue

            # Wait for next interval
            time.sleep(self.interval)


def load_config():
    """
    Load configuration from ~/.molbox_tester file.

    Returns:
        dict: Configuration dictionary with keys: host, port, interval, command
    """
    config_path = Path.home() / ".molbox_tester"
    
    # Default configuration
    config = {
        'host': 'localhost',
        'port': 23,
        'interval': 2.0,
        'command': 'ALLR',
        'timeout': 10
    }

    if config_path.exists():
        logger.info(f"Loading configuration from {config_path}")
        parser = ConfigParser()
        parser.read(config_path)

        if 'molbox' in parser:
            section = parser['molbox']
            config['host'] = section.get('host', config['host'])
            config['port'] = int(section.get('port', config['port']))
            config['interval'] = float(section.get('interval', config['interval']))
            config['command'] = section.get('command', config['command'])
            config['timeout'] = int(section.get('timeout', config['timeout']))
    else:
        logger.info(f"No configuration file found at {config_path}, using defaults")
        logger.info(f"You can create a configuration file with the following format:")
        logger.info("[molbox]")
        logger.info("host = localhost")
        logger.info("port = 23")
        logger.info("interval = 2.0")
        logger.info("command = ALLR")
        logger.info("timeout = 10")

    return config


def main():
    """Main entry point for the molbox command."""
    try:
        config = load_config()
        tester = MolboxTester(
            host=config['host'],
            port=config['port'],
            interval=config['interval'],
            command=config['command'],
            timeout=config['timeout']
        )
        tester.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
