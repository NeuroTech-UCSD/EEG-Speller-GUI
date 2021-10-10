# EEG-Speller
EEG Speller is an application desgined to give users the ability to spell words without a physical keyboard. Brain signals are read from an EEG headset and are then decoded using machine-learning to classify the particular character the user wants to select. This application specifically focuses on motor-imagery based speller and aims to deliver a novel graphical-user interface that would improve the performance and speed of character selection.

## MOTOR IMAGERY GUI
The GUI consists of an inner and outer circle that has three layers. Each layer is spliced into 4 parts or subsections (tubes). The inner layers have 5 letters in each subsection resulting in a total of 20 letters in the inner layer. The outer layer also consists of 5 letters in each subsection. The purpose of the outer layer is to provide the users easier access to characters that they will most likely select. These characters are generated based on our text-generation NLP model.

<img width="519" alt="Screen Shot 2021-10-10 at 1 17 28 PM" src="https://user-images.githubusercontent.com/45252772/136711826-1f7b6ee9-eb60-4ba5-8760-f06b840c8c1d.png">


### The Process: 
1. GUI Starts from the upper right subsection and rotates every 5 seconds
2. Rotation will continue between the subsections until the user chooses a particular subsection through a right-imagined movement (motor-imagery task)
3. When the subsection is selected, the GUI will now focus on the characters along the wedge and rotate through the characters one by one
4. The user will then pick the character through a right imagined movement (motor-imagery task)
5. After the user has picked a character, 5 characters will appear in the outer layer of the same subsection. These 5 characters are the most likely characters to be selected based on our NLP model. The user can then easily move to the outer layer in one step as opposed to using multiple steps to pick a character in the inner layer. 
6. Note that a left-imagined movement is dedicated to reverting a decision

Characters selected are saved in a typing window next to GUI window.<br>
![ezgif com-gif-maker_1](https://user-images.githubusercontent.com/74154666/136670650-fa3f735b-c464-49ea-907b-90c69bea6d10.gif)<br>

## P300/SSVEP GUI
This GUI consists of four 3x3 character matrices, totaling 36 characters. Each submatrix flashes at its own frequency, recognized by the SSVEP signal, while there is identical pattern of these flashing characters through each individual matrix, recognized by the P300 potential signal. <br>

<img width="917" alt="Screen Shot 2021-10-09 at 1 17 16 PM" src="https://user-images.githubusercontent.com/74033651/136673378-5f853c3b-7234-41dd-b59f-691dc6193706.png">
<br>

The GUI follows this pattern: 
* The top left character begins flashing at its submatrix's respective frequency.
* After X ms, the next character begins to flash at the same frequency as the previous. There will be two characters flashing at once per submatrix.
* This pattern continues until the end of the round. <br>

![giphy](https://user-images.githubusercontent.com/74033651/136673422-3af96b30-8204-42db-b86b-e05a9b72ac05.gif)

<br>

The user's instruction is to locate their desired character on the supermatrix and notice when it begins to flash. It should then get selected once that round is over. 

## Contributors
Chao-Li Wei, Eugene Kim, Andrew Clinton Wong, Joelle Faybishenko, Nova Lee, Quinton Ramaswamy, Simon Fei, Bailey Man
