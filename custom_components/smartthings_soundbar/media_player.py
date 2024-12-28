import logging
import voluptuous as vol

from .api import SoundbarApi

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    PLATFORM_SCHEMA,
)
from homeassistant.const import (
    CONF_NAME, CONF_API_KEY, CONF_DEVICE_ID
)
import homeassistant.helpers.config_validation as cv

# Check for the availability of MediaPlayerDeviceClass
try:
    from homeassistant.components.media_player.const import MediaPlayerDeviceClass
    HAS_MEDIAPLAYERDEVICECLASS = True
except ImportError:
    HAS_MEDIAPLAYERDEVICECLASS = False

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "SmartThings Soundbar"
CONF_MAX_VOLUME = "max_volume"

SUPPORT_SMARTTHINGS_SOUNDBAR = (
        MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DEVICE_ID): cv.string,
        vol.Optional(CONF_MAX_VOLUME, default=1): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the platform for the SmartThings Soundbar."""
    name = config.get(CONF_NAME)
    api_key = config.get(CONF_API_KEY)
    device_id = config.get(CONF_DEVICE_ID)
    max_volume = config.get(CONF_MAX_VOLUME)
    add_entities([SmartThingsSoundbarMediaPlayer(name, api_key, device_id, max_volume)])


class SmartThingsSoundbarMediaPlayer(MediaPlayerEntity):
    """Representation of a SmartThings Soundbar as a media player entity."""

    def __init__(self, name, api_key, device_id, max_volume):
        """Initialize the SmartThings Soundbar media player entity."""
        self._name = name
        self._device_id = device_id
        self._api_key = api_key
        self._max_volume = max_volume
        self._volume = 1
        self._muted = False
        self._playing = True
        self._state = "on"
        self._source = ""
        self._source_list = []
        self._media_title = ""

    def update(self):
        """Update the state of the soundbar from the API."""
        SoundbarApi.device_update(self)

    @property
    def unique_id(self) -> str | None:
        """Return the unique ID for this entity."""
        return f"SmartThings_Soundbar_{self._device_id}"

    def turn_off(self):
        """Turn off the soundbar."""
        arg = ""
        cmdtype = "switch_off"
        SoundbarApi.send_command(self, arg, cmdtype)

    def turn_on(self):
        """Turn on the soundbar."""
        arg = ""
        cmdtype = "switch_on"
        SoundbarApi.send_command(self, arg, cmdtype)

    def set_volume_level(self, arg, cmdtype="setvolume"):
        """Set the volume level of the soundbar."""
        SoundbarApi.send_command(self, arg, cmdtype)

    def mute_volume(self, mute, cmdtype="audiomute"):
        """Mute or unmute the soundbar."""
        SoundbarApi.send_command(self, mute, cmdtype)

    def volume_up(self, cmdtype="stepvolume"):
        """Increase the volume of the soundbar."""
        arg = "up"
        SoundbarApi.send_command(self, arg, cmdtype)

    def volume_down(self, cmdtype="stepvolume"):
        """Decrease the volume of the soundbar."""
        arg = ""
        SoundbarApi.send_command(self, arg, cmdtype)

    def select_source(self, source, cmdtype="selectsource"):
        """Select the input source for the soundbar."""
        SoundbarApi.send_command(self, source, cmdtype)

    def select_sound_mode(self, sound_mode):
        """Select the sound mode for the soundbar."""
        SoundbarApi.send_command(self, sound_mode, "selectsoundmode")

    @property
    def device_class(self):
        """
        Return the class of the device.

        Use MediaPlayerDeviceClass.SPEAKER if available, otherwise fall back
        to the legacy DEVICE_CLASS_SPEAKER.
        """
        return (
            MediaPlayerDeviceClass.SPEAKER
            if HAS_MEDIAPLAYERDEVICECLASS
            else "speaker"  # Fallback for older versions of Home Assistant
        )

    @property
    def supported_features(self):
        """Return the features supported by the soundbar."""
        return SUPPORT_SMARTTHINGS_SOUNDBAR

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def media_title(self):
        """Return the title of the currently playing media."""
        return self._media_title

    def media_play(self):
        """Send the play command to the soundbar."""
        arg = ""
        cmdtype = "play"
        SoundbarApi.send_command(self, arg, cmdtype)

    def media_pause(self):
        """Send the pause command to the soundbar."""
        arg = ""
        cmdtype = "pause"
        SoundbarApi.send_command(self, arg, cmdtype)

    @property
    def state(self):
        """Return the state of the soundbar."""
        return self._state

    @property
    def is_volume_muted(self):
        """Return whether the soundbar volume is muted."""
        return self._muted

    @property
    def volume_level(self):
        """Return the volume level of the soundbar."""
        return self._volume

    @property
    def source(self):
        """Return the current input source."""
        return self._source

    @property
    def source_list(self):
        """Return the list of available input sources."""
        return self._source_list
