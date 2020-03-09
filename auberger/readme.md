Requirements:

Download m4m8, take all folders from inside the folder "Python Scripts" and add
them to your MIDI Remote Scripts folder inside the Live application bundle.  Their
are more detailed instructions about installing m4m8 in its corresponding readme, but
it's not necessary to install anything from it beyond the Python Scripts.

Take the "STEPSEQ" folder from this this project and place and add
it to your MIDI Remote Scripts folder inside the Live application bundle.

Install the STEPSEQ.jzml file to your iPad's Lemur application.  There are multiple
ways to do this, the method I find easiest is to load it in the Lemur editor and then
sync the application to your device while Lemur is running.  Make sure to save the file
locally on your Lemur when you've finished laoding it.

In Lemur's setup screen, you'll need to make sure that it's first input and output
correspond to the virtual input and output on your computer.  

Make sure to restart Live so that it recognizes and compiles the new Python Scripts
you've just installed.

In Live's MIDI preferences, add a new control surface (STEPSEQ) to one of its control
surface slots, and set it's input and output to the Lemurs input and output.  Make
sure to enable both "Remote" and "Track" for the control surfaces inputs AND outputs.
