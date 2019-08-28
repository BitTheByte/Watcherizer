# Watcherizer
Slack Bot to monitor websites for code changes, special thanks to [@k3r1it0](https://github.com/k3r1it0) for suggesting this idea
![](https://i.ibb.co/ySG2r6v/Untitled-1.png)  


# Slack Setup
You'll need to create a [slack bot](https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace) after that navigate to your bot dashboard and to `Slack Commands` tab then add the following commands


| Command    	| Description                             	| Request URL                                     
|------------	|-----------------------------------------	|-------------------------------------------------
| /watch     	| Add a website to the watching list      	| https://your-ip.host:1337/monitor   
| /list      	| Lists file(s) which are being monitored 	| https://your-ip.host:1337/list
| /unwatch   	| Stop watching for changes               	| https://your-ip.host:1337/remove
| /watchfreq 	| Set/Get watching frequency              	| https://your-ip.host:1337/watchtime
  
&nbsp;

Your slack commands should look like this    

![Slack Commands](https://i.ibb.co/SPz055x/slack-commands.png)


# Server Setup
### Requirements
- Python 3.7
- Online RDP/VPS



Go to your slack bot dashboard, click on `OAuth & Permissions` And open `watcherizer.py` with your editor of choice then change line [#23](https://github.com/BitTheByte/Watcherizer/blob/master/watcherizer.py#L23) to `Slack Channel ID` and 
line [#24](https://github.com/BitTheByte/Watcherizer/blob/master/watcherizer.py#L24) to `Bot User OAuth Access Token`

You will also need to install python third party libraries using the following command:
```
$ sudo python3 -m pip install -r requirements.txt
```

Now you're ready to run the bot on your system
```
$ python3 watcherizer.py
```

if everything is ok your should see this message on your slack channel   

![](https://i.ibb.co/N1dB3Tx/Capture.png)


# Examples

### Slack commands 
- Adding target to the watching list

```
/watch https://mytarget.com
```
- Removing target from the watching list

```
/unwatch https://mytarget.com
```
- List targets on the watching list

```
/list
```
- Get the watching frequency

```
/watchfreq
```
- Set the watching frequency

```
/watchfreq 3600
```

### Reporting 
- Javascript file changed

![](https://i.ibb.co/r0Trnyw/report-example2.png)

- HTML body changed

![](https://i.ibb.co/6wZJhkT/report-example3.png)

- Adding/Removing javascript files  

![](https://i.ibb.co/7Nq0t4w/Capture2.png)
