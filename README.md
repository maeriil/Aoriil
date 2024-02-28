# Aoriil

Aoriil is meant to be a upcoming chrome extension that can easily machine translate an untranslated mangas found online. The design of this program is that it will take in any untranslated manga image/pdf and produce an english translated text for each bubble to the best of its ability. 

# Comparision
Below is the sample image of the current stage of the program. Original is the japanese/korean/chinese version of the manga panel. Original English Translated is the hand translated to english, either by some publications or manually by contributors of manga scan community. Finally, Aoriil Machine Translated is our program attempting to translated the panel to its best ability. 
(Note: The green bounding boxes are added to the output image for display purposes to understand the limitations of the program)

| Original  | Original English Translated | Aoriil Machine Translated |
|:-------------------------:|:-------------------------:|:-------------------------:|
| ![japanese4](https://github.com/maeriil/Aoriil/assets/104389763/b11ae6bf-cf92-4fc5-b9bc-279575acc54c) | ![image (4)](https://github.com/maeriil/Aoriil/assets/104389763/c9140e1e-899b-4afc-aa9b-2f3c8a9f5b1e) | ![translated-mock](https://github.com/maeriil/Aoriil/assets/104389763/790c2aed-2ce4-4260-ada6-e0696bf7b0c3) |
| ![japanese5](https://github.com/maeriil/Aoriil/assets/104389763/2473637d-17e0-44b8-9349-8cc516c5e955) | unknown.. | ![translated-mock (1)](https://github.com/maeriil/Aoriil/assets/104389763/8b285189-e401-4142-a110-1df2e0ae9b6a) |
| ![image (2)](https://github.com/maeriil/Aoriil/assets/104389763/7c78637f-642c-40aa-bab4-d5d228a75482) | ![image (1)](https://github.com/maeriil/Aoriil/assets/104389763/3b7fecdf-bbff-40ed-b0b8-6b4903ba1dbf) | ![translated-mock](https://github.com/maeriil/Aoriil/assets/104389763/f36f9e50-86d6-4978-ab91-a4a7e3e73741)

# Program Limitations
Despite few bugs seen in the image above, the output image is very legiable to the point that the program can be used to translate few panels. There are however, some limitations to this program that will be further addressed below. 

- The first challenge to this project was figuring out a proper bounding box for the detected texts. Sometimes, it is the case that two or more bounding boxes are "merged" because they are so close to each other that the program thinks they are part of the same text! See the example below. ![borderim1](https://github.com/maeriil/Aoriil/assets/104389763/efd39564-3235-45c3-b4ae-653a30949615) Ignoring the rotation, we can see that there is a speech bubble whose text has been merged alongside the texts in the background. This is an issue since the speech bubble has now lost its meaning and thus will be translated completely incorrectly. While this issue has not been completely resolved yet, it has improved a lot and one of the reasons is because the image is rotated counterclockwise 90 degrees and so the optical character detection library is able to detect and seperate the characters much better.
- The next limitation is that on many of the websites, in order to counter the rampant issue of downloading images, they have jumbled up the original image in the website before displaying it to the users. An example of what it looks like is this: ![limitation](https://github.com/maeriil/Aoriil/assets/104389763/31d236b9-84c8-450f-911e-4bd532c4c194) As we can see in the above image, it is completely unreadable! The websites internally will repatch these image before displaying to user. Another example of this is: ![image (3)](https://github.com/maeriil/Aoriil/assets/104389763/6e33c74b-11c8-4d5f-b326-4e4138575470)

# Improvements Made
There has been many improvements made to this program in order to translate better and better
- Image processing techniques such as applying gaussian blurs, sharpening, cropping, etc are used to better detect and translate the characters.
- The green bounding box originally are detected like this: ![image (5)](https://github.com/maeriil/Aoriil/assets/104389763/1f4e6fa6-77da-4c07-bd83-c699b85c69d4) However, individually translating each boxes is incorrect; in general, the speech bubble would lose its meaning since there is no transition from one box to another, even if they are part of the same speech bubble. Therefore, we use our own bounding box merging algorithm to get our result as this: ![borderim1 (1)](https://github.com/maeriil/Aoriil/assets/104389763/e92ccd66-56ab-4bfc-9b31-e3786a539b52)

# Next things to work on..
The backend is in a pretty stable and working state so our current priority now should be to work on the chrome extension. One of the biggest challenge we are facing is that we need to grab all the images in the website and next one is replacing the existing website image to our translated one..




