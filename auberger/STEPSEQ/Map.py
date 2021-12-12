# by amounra 0220 : http://www.aumhaa.com
# written against Live 10.1.7 release


from ableton.v2.control_surface.elements.color import Color
from aumhaa.v2.livid.colors import *

"""
STEPSEQ Map.py

Created by amounra on 2020-2-25.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right;
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""

CHANNEL = 0
ENCODER_CHANNEL = 2
BUTTON_CHANNEL = 1
PAD_CHANNEL = 0
MIXER_SESSION_CHANNEL = 3

STEPSEQ_PADS = list(range(128))
STEPSEQ_BUTTONS = list(range(8))
STEPSEQ_ENCODERS = list(range(4))
STEPSEQ_ENCODER_BUTTONS = list(range(4))
STEPSEQ_SESSION_BUTTONS = list(range(34))
STEPSEQ_MIXER_BUTTONS = list(range(34,42))
STEPSEQ_MIXER_SLIDERS = list(range(8))

COLOR_MAP = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

NOTEBANKS = [list(range(32)), list(range(32,64)), list(range(64,96)), list(range(96,128))]
TRIPLET_NOTEBANKS = [[0,1,2,3,4,5,6,7,8,9,10,11,12,16,17,18,19,20,21,22,23,24,25,26,27],
			[32,33,34,35,36,37,38,39,40,41,42,43,48,49,50,51,52,53,54,55,56,57,58,59],
			[64,65,66,67,68,69,70,71,72,73,74,75,80,81,82,83,84,85,86,87,88,89,90,91],
			[96,97,98,99,100,101,102,103,104,105,106,107,112,113,114,115,116,117,118,119,120,121,122,123]]

"""The values in this array determine the choices for what length of clip is created when "Fixed Length" is turned on:
0 = 1 Beat
1 = 2 Beat
2 = 1 Bar
3 = 2 Bars
4 = 4 Bars
5 = 8 Bars
6 = 16 Bars
7 = 32 Bars
"""
LENGTH_VALUES = [2, 3, 4]

class SSRGB:

	OFF = MonoColor(0)
	white = MonoColor(1)
	yellow = MonoColor(2)
	cyan = MonoColor(3)
	magenta = MonoColor(4)
	red = MonoColor(5)
	green = MonoColor(6)
	blue = MonoColor(7)
	WHITE = MonoColor(8)
	YELLOW = MonoColor(9)
	CYAN = MonoColor(10)
	MAGENTA = MonoColor(11)
	RED = MonoColor(12)
	GREEN = MonoColor(13)
	BLUE = MonoColor(14)


class STEPSEQColors:


	class DefaultButton:
		On = LividRGB.WHITE
		Off = LividRGB.OFF
		Disabled = LividRGB.OFF
		Alert = LividRGB.BlinkFast.WHITE


	class SequenceSelector:
		Selected = LividRGB.WHITE
		Unselected = LividRGB.OFF


	class SequenceColors:
		Sequence0 = SSRGB.YELLOW
		Sequence1 = SSRGB.CYAN
		Sequence2 = SSRGB.MAGENTA
		Sequence3 = SSRGB.RED
		Sequence4 = SSRGB.GREEN
		Sequence5 = SSRGB.BLUE
		Sequence6 = SSRGB.YELLOW
		Sequence7 = SSRGB.CYAN


	class MainModes:
		Clips = LividRGB.WHITE
		Clips_shifted = LividRGB.BlinkFast.WHITE
		Sends = LividRGB.MAGENTA
		Sends_shifted = LividRGB.BlinkFast.MAGENTA
		Device = LividRGB.CYAN
		Device_shifted = LividRGB.BlinkFast.CYAN
		User = LividRGB.RED
		User_shifted = LividRGB.BlinkFast.RED


	class Session:
		StopClipTriggered = LividRGB.BlinkFast.BLUE
		StopClip = LividRGB.BLUE
		Scene = LividRGB.CYAN
		NoScene = LividRGB.OFF
		SceneTriggered = LividRGB.BlinkFast.BLUE
		ClipTriggeredPlay = LividRGB.BlinkFast.GREEN
		ClipTriggeredRecord = LividRGB.BlinkFast.RED
		RecordButton = LividRGB.OFF
		ClipEmpty = LividRGB.OFF
		ClipStopped = LividRGB.WHITE
		ClipStarted = LividRGB.GREEN
		ClipRecording = LividRGB.RED
		NavigationButtonOn = LividRGB.BLUE
		PageNavigationButtonOn = LividRGB.CYAN
		Empty = LividRGB.OFF


	class NoteEditor0:

		class Step:
			Low = SSRGB.YELLOW
			High = SSRGB.YELLOW
			Full = SSRGB.YELLOW
			Muted = SSRGB.YELLOW
			StepEmpty = SSRGB.yellow


		class StepEditing:
			High = SSRGB.YELLOW
			Low = SSRGB.YELLOW
			Full = SSRGB.YELLOW
			Muted = SSRGB.YELLOW


		StepEmpty = SSRGB.yellow
		StepEmptyBase = SSRGB.yellow
		StepEmptyScale = SSRGB.yellow
		StepDisabled = SSRGB.yellow
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF


	class NoteEditor1:

		class Step:
			Low = SSRGB.CYAN
			High = SSRGB.CYAN
			Full = SSRGB.CYAN
			Muted = SSRGB.CYAN
			StepEmpty = SSRGB.cyan


		class StepEditing:
			High = SSRGB.CYAN
			Low = SSRGB.CYAN
			Full = SSRGB.CYAN
			Muted = SSRGB.CYAN


		StepEmpty = SSRGB.cyan
		StepEmptyBase = SSRGB.cyan
		StepEmptyScale = SSRGB.cyan
		StepDisabled = SSRGB.cyan
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor2:

		class Step:
			Low = SSRGB.MAGENTA
			High = SSRGB.MAGENTA
			Full = SSRGB.MAGENTA
			Muted = SSRGB.MAGENTA
			StepEmpty = SSRGB.magenta


		class StepEditing:
			High = SSRGB.MAGENTA
			Low = SSRGB.MAGENTA
			Full = SSRGB.MAGENTA
			Muted = SSRGB.MAGENTA


		StepEmpty = SSRGB.magenta
		StepEmptyBase = SSRGB.magenta
		StepEmptyScale = SSRGB.magenta
		StepDisabled = SSRGB.magenta
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor3:

		class Step:
			Low = SSRGB.GREEN
			High = SSRGB.GREEN
			Full = SSRGB.GREEN
			Muted = SSRGB.GREEN
			StepEmpty = SSRGB.green


		class StepEditing:
			High = SSRGB.GREEN
			Low = SSRGB.GREEN
			Full = SSRGB.GREEN
			Muted = SSRGB.GREEN


		StepEmpty = SSRGB.green
		StepEmptyBase = SSRGB.green
		StepEmptyScale = SSRGB.green
		StepDisabled = SSRGB.green
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor4:

		class Step:
			Low = SSRGB.RED
			High = SSRGB.RED
			Full = SSRGB.RED
			Muted = SSRGB.RED
			StepEmpty = SSRGB.red


		class StepEditing:
			High = SSRGB.RED
			Low = SSRGB.RED
			Full = SSRGB.RED
			Muted = SSRGB.RED


		StepEmpty = SSRGB.red
		StepEmptyBase = SSRGB.red
		StepEmptyScale = SSRGB.red
		StepDisabled = SSRGB.red
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor5:

		class Step:
			Low = SSRGB.BLUE
			High = SSRGB.BLUE
			Full = SSRGB.BLUE
			Muted = SSRGB.BLUE
			StepEmpty = SSRGB.blue


		class StepEditing:
			High = SSRGB.BLUE
			Low = SSRGB.BLUE
			Full = SSRGB.BLUE
			Muted = SSRGB.BLUE


		StepEmpty = SSRGB.blue
		StepEmptyBase = SSRGB.blue
		StepEmptyScale = SSRGB.blue
		StepDisabled = SSRGB.blue
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor6:

		class Step:
			Low = SSRGB.YELLOW
			High = SSRGB.YELLOW
			Full = SSRGB.YELLOW
			Muted = SSRGB.YELLOW
			StepEmpty = SSRGB.yellow


		class StepEditing:
			High = SSRGB.YELLOW
			Low = SSRGB.YELLOW
			Full = SSRGB.YELLOW
			Muted = SSRGB.YELLOW


		StepEmpty = SSRGB.yellow
		StepEmptyBase = SSRGB.yellow
		StepEmptyScale = SSRGB.yellow
		StepDisabled = SSRGB.yellow
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor7:

		class Step:
			Low = SSRGB.CYAN
			High = SSRGB.CYAN
			Full = SSRGB.CYAN
			Muted = SSRGB.CYAN
			StepEmpty = SSRGB.cyan


		class StepEditing:
			High = SSRGB.CYAN
			Low = SSRGB.CYAN
			Full = SSRGB.CYAN
			Muted = SSRGB.CYAN


		StepEmpty = SSRGB.cyan
		StepEmptyBase = SSRGB.cyan
		StepEmptyScale = SSRGB.cyan
		StepDisabled = SSRGB.cyan
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = SSRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class NoteEditor:

		class Step:
			Low = LividRGB.CYAN
			High = LividRGB.BLUE
			Full = LividRGB.YELLOW
			Muted = LividRGB.YELLOW
			StepEmpty = LividRGB.OFF


		class StepEditing:
			High = LividRGB.GREEN
			Low = LividRGB.CYAN
			Full = LividRGB.YELLOW
			Muted = LividRGB.WHITE


		StepEmpty = LividRGB.OFF
		StepEmptyBase = LividRGB.OFF
		StepEmptyScale = LividRGB.OFF
		StepDisabled = LividRGB.OFF
		Playhead = SSRGB.WHITE
		PlayheadRecord = SSRGB.RED
		StepSelected = LividRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.OFF

	class LoopSelector:
		Playhead = SSRGB.WHITE
		OutsideLoop = LividRGB.WHITE
		InsideLoopStartBar = LividRGB.CYAN
		SelectedPage = LividRGB.MAGENTA
		InsideLoop = LividRGB.BLUE
		PlayheadRecord = SSRGB.RED


	class DrumGroup:
		PadAction = LividRGB.WHITE
		PadFilled = LividRGB.GREEN
		PadFilledAlt = LividRGB.MAGENTA
		PadSelected = LividRGB.WHITE
		PadSelectedNotSoloed = LividRGB.WHITE
		PadEmpty = LividRGB.OFF
		PadMuted = LividRGB.YELLOW
		PadSoloed = LividRGB.CYAN
		PadMutedSelected = LividRGB.BLUE
		PadSoloedSelected = LividRGB.BLUE
		PadInvisible = LividRGB.OFF
		PadAction = LividRGB.RED


	class Mixer:
		SoloOn = LividRGB.CYAN
		SoloOff = LividRGB.OFF
		MuteOn = LividRGB.YELLOW
		MuteOff = LividRGB.OFF
		ArmSelected = LividRGB.GREEN
		ArmUnselected = LividRGB.RED
		ArmOff = LividRGB.OFF
		StopClip = LividRGB.BLUE
		SelectedOn = LividRGB.BLUE
		SelectedOff = LividRGB.OFF


	class Recording:
		On = LividRGB.BlinkFast.GREEN
		Off = LividRGB.GREEN
		Transition = LividRGB.BlinkSlow.GREEN


	class Recorder:
		On = LividRGB.WHITE
		Off = LividRGB.BLUE
		NewOn = LividRGB.BlinkFast.YELLOW
		NewOff = LividRGB.YELLOW
		FixedOn = LividRGB.BlinkFast.CYAN
		FixedOff = LividRGB.CYAN
		RecordOn = LividRGB.BlinkFast.GREEN
		RecordOff = LividRGB.GREEN
		FixedAssigned = LividRGB.MAGENTA
		FixedNotAssigned = LividRGB.OFF
		OverdubOn = LividRGB.BlinkFast.RED
		OverdubOff = LividRGB.RED


	class Transport:
		OverdubOn = LividRGB.BlinkFast.RED
		OverdubOff = LividRGB.RED
		StopOn = LividRGB.BLUE
		StopOff = LividRGB.BLUE


	class Sequencer:
		OctaveOn = LividRGB.BlinkFast.CYAN
		OctaveOff = LividRGB.OFF
		On = LividRGB.WHITE
		Off = LividRGB.OFF


	class Device:
		NavOn = LividRGB.MAGENTA
		NavOff = LividRGB.OFF
		BankOn = LividRGB.YELLOW
		BankOff = LividRGB.OFF
		ChainNavOn = LividRGB.RED
		ChainNavOff = LividRGB.OFF
		ContainNavOn = LividRGB.CYAN
		ContainNavOff = LividRGB.OFF


	class DeviceNavigator:
		DevNavOff = LividRGB.OFF
		DevNavOn = LividRGB.MAGENTA
		ChainNavOn = LividRGB.RED
		ChainNavOff = LividRGB.OFF
		LevelNavOn = LividRGB.CYAN
		LevelNavOff = LividRGB.OFF


	class MonoInstrument:

		PressFlash = LividRGB.WHITE
		OffsetOnValue = LividRGB.GREEN
		OffsetOffValue = LividRGB.OFF
		ScaleOffsetOnValue = LividRGB.RED
		ScaleOffsetOffValue = LividRGB.OFF
		SplitModeOnValue = LividRGB.WHITE
		SplitModeOffValue = LividRGB.OFF
		SequencerModeOnValue = LividRGB.CYAN
		SequencerModeOffValue = LividRGB.OFF
		DrumOffsetOnValue = LividRGB.MAGENTA
		DrumOffsetOffValue = LividRGB.OFF
		VerticalOffsetOnValue = LividRGB.BLUE
		VerticalOffsetOffValue = LividRGB.OFF

		class Keys:
			SelectedNote = LividRGB.GREEN
			RootWhiteValue = LividRGB.RED
			RootBlackValue = LividRGB.MAGENTA
			WhiteValue = LividRGB.CYAN
			BlackValue = LividRGB.BLUE


		class Drums:
			SelectedNote = LividRGB.BLUE
			EvenValue = LividRGB.GREEN
			OddValue = LividRGB.MAGENTA
