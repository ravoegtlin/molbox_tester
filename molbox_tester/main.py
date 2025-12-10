#!/usr/bin/env python3
"""
Main module for molbox_tester.

Connects to a host via telnet, sends commands periodically, and logs responses.
Implements timeout handling and automatic reconnection.

Uses telnetlib3 for modern async telnet support.
"""

import asyncio
import logging
import sys
from pathlib import Path
from configparser import ConfigParser
import telnetlib3


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
        self.reader = None
        self.writer = None

    async def connect(self):
        """Establish telnet connection to the host."""
        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")
            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(self.host, self.port),
                timeout=self.timeout
            )
            logger.info("Connected successfully")
            return True
        except asyncio.TimeoutError:
            logger.error(f"Connection timeout after {self.timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Close the telnet connection."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
                logger.info(f"Disconnected from {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.reader = None
                self.writer = None

    async def send_command(self):
        """
        Send command and read response.

        Returns:
            bool: True if successful, False if timeout or error occurred
        """
        try:
            # Send command
            command_str = self.command + "\r\n"
            self.writer.write(command_str)
            await self.writer.drain()
            logger.info(f"Sent: {self.command}")

            # Read response with timeout
            response = await asyncio.wait_for(
                self.reader.readline(),
                timeout=self.timeout
            )
            
            response_str = response.strip()
            logger.info(f"Received: {response_str}")
            return True

        except asyncio.TimeoutError:
            logger.warning("No response received within timeout")
            return False
        except asyncio.IncompleteReadError:
            logger.error("Connection closed by remote host")
            return False
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False

    async def run(self):
        """Main loop: send commands periodically with reconnection logic."""
        logger.info("Starting molbox_tester...")
        logger.info(f"Configuration: host={self.host}, port={self.port}, "
                   f"interval={self.interval}s, command={self.command}, timeout={self.timeout}s")

        while True:
            # Ensure we're connected
            if not self.writer:
                if not await self.connect():
                    logger.warning(f"Retrying connection in {self.interval} seconds...")
                    await asyncio.sleep(self.interval)
                    continue

            # Send command and handle response
            success = await self.send_command()
            
            if not success:
                # Timeout or error occurred, reconnect
                logger.warning("Reconnecting due to timeout or error...")
                await self.disconnect()
                if not await self.connect():
                    logger.warning(f"Reconnection failed, retrying in {self.interval} seconds...")
                    await asyncio.sleep(self.interval)
                    continue

            # Wait for next interval
            await asyncio.sleep(self.interval)


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


async def async_main():
    """Async main entry point for the molbox command."""
    config = load_config()
    tester = MolboxTester(
        host=config['host'],
        port=config['port'],
        interval=config['interval'],
        command=config['command'],
        timeout=config['timeout']
    )
    await tester.run()


def main():
    """Main entry point for the molbox command."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
