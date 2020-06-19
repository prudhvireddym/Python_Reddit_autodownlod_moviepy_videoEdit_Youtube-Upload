### Python Reddit Autodownlod,Video edit with moviepy finally upload to Youtube
##### This is one of the complex projects i had undertaken during the quarentine. It involved like a series of 3 small projects merged together to form the complete project. As from the title this project involves the following steps.

* First to run run the following command "python reddit_linux.py --url="day/month/week/year" --subreddit="(any_subreddit_name)watchpeopledieinside" --now="1""
  * The argument --url - It is used to set to get either the top post of either the day or week or month or year
  * The argument --subreddit - Is used to specify the subreddit to get the videos from 
  * The argument --now - It is used to either exicute the code right now if set to "1" else if is set to anything else it will get exicuted at the time specified in the script
  
 ####Tasks Done by the code
 
 1. Scrape the subreddit mentioned and download all the videos can specify the no of videos to download in the code. Reddit does not store all the video and audio in the same pace so i had to use a third party website to download the videos. It also scrapes the username and also the video name along withthe video title and stores it in the name of the downoaded file.
 2. Next it edits the video by adding 

