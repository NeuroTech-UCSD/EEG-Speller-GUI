# EEG-Speller
EEG speller help people that cannot use keyboard to type words using EEG headsets.

## Github Directories

## GUI
GUI consists of two circles that have three layers (tubes) and sliced in a quarter (wedge). The middle tube have 5 letters in each wedge, 20 letters in the circle. The outer tube also consists of 5 letters in each wedge. It will be initialized blank for prediction letters. When a letter is selected, 5 following prediction letters will show up in the outer tube of its wedge.
Inner circle is deleate feature, which will delete the latest letter selected in our typing window.
![Screen Shot 2021-10-09 at 10 53 13 AM](https://user-images.githubusercontent.com/74154666/136669174-a026dbea-41c6-4394-b097-f04ef3d24f80.png)
![Screen Shot 2021-10-09 at 10 53 19 AM](https://user-images.githubusercontent.com/74154666/136669177-a33cbc17-ffee-405e-8c93-9cfa3db643e1.png)
GUI starts from the upper right wedges and rotates every 5 seconds. Then rotation will continue between tubes after choosing a wedge. When a certain tube is selected, it will now rotate between the 5 letters. A letter selected will trigger a new update of its outer tube to 5 prediction and will start with rotating between 5 predicted letters. 

GUI Usage
Right is to select and left goes back to last step.

Characters selected are saved in a typing window next to GUI window.
