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
STEPSEQ_PADS = range(128)
STEPSEQ_BUTTONS = range(8)
STEPSEQ_ENCODERS = range(4)
STEPSEQ_ENCODER_BUTTONS = range(4)

COLOR_MAP = [2, 64, 4, 8, 16, 127, 32]

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

class STEPSEQColors:


	class DefaultButton:
		On = LividRGB.WHITE
		Off = LividRGB.OFF
		Disabled = LividRGB.OFF
		Alert = LividRGB.BlinkFast.WHITE


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


	class NoteEditor:

		class Step:
			Low = LividRGB.CYAN
			High = LividRGB.WHITE
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
		Playhead = Color(31)
		PlayheadRecord = Color(31)
		StepSelected = LividRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.MAGENTA


	class LoopSelector:
		Playhead = LividRGB.YELLOW
		OutsideLoop = LividRGB.BLUE
		InsideLoopStartBar = LividRGB.CYAN
		SelectedPage = LividRGB.WHITE
		InsideLoop = LividRGB.CYAN
		PlayheadRecord = LividRGB.RED


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


	class Mod:
		class Nav:
			OnValue = LividRGB.RED
			OffValue = LividRGB.WHITE



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




	class Translation:

		SelectorOn = LividRGB.WHITE
		SelectorOff = LividRGB.OFF

		class Channel_10:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF


		class Channel_11:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF


		class Channel_12:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF


		class Channel_13:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF
