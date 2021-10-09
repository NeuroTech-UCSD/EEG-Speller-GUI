# EEG-Speller
EEG speller help people that cannot use keyboard to type words using EEG headsets.

## MOTOR IMAGERY GUI
GUI consists of two circles that have three layers (tubes) and sliced in a quarter (wedge). The middle tube have 5 letters in each wedge, 20 letters in the circle. The outer tube also consists of 5 letters in each wedge. It will be initialized blank for prediction letters. When a letter is selected, 5 following prediction letters will show up in the outer tube of its wedge.
Inner circle is deleate feature, which will delete the latest letter selected in our typing window.<br>
![Screen Shot 2021-10-09 at 11 13 48 AM](https://user-images.githubusercontent.com/74154666/136669741-7cb8cd48-d857-494f-9479-cf2fd3480344.png)
<br>
* GUI starts from the upper right wedges and rotates every 5 seconds. 
* Rotation will continue between tubes after choosing a wedge. 
* When a certain tube is selected, it will now rotate between the 5 letters. 
* A letter selected will trigger a new update of its outer tube to 5 prediction and will start with rotating between 5 predicted letters. 

GUI Usage
Right is to select and left goes back to last step.

Characters selected are saved in a typing window next to GUI window.<br>
![ezgif com-gif-maker_1](https://user-images.githubusercontent.com/74154666/136670650-fa3f735b-c464-49ea-907b-90c69bea6d10.gif)<br>

## P300/SSVEP GUI
This GUI consists of four 3x3 character matrices, totaling 36 characters. Each submatrix flashes at its own frequency, recognized by the SSVEP signal, while there is identical pattern of these flashing characters through each individual matrix, recognized by the P300 potential signal. 
<img width="917" alt="Screen Shot 2021-10-09 at 1 17 16 PM" src="https://user-images.githubusercontent.com/74033651/136673378-5f853c3b-7234-41dd-b59f-691dc6193706.png">
<br>

The GUI follows this pattern: 
* The top left character begins flashing at its submatrix's respective frequency.
* After X ms, the next character begins to flash at the same frequency as the previous. There will be two characters flashing at once per submatrix.
* This pattern continues until the end of the round. <br>

![giphy](https://user-images.githubusercontent.com/74033651/136673422-3af96b30-8204-42db-b86b-e05a9b72ac05.gif)

<br>

The user's instruction is to locate their desired character on the supermatrix and notice when it begins to flash. It should then get selected once that round is over. 
