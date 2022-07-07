function lookForHost(meetinglist){
    for(let i =0; i < meetinglist.length;i++){
        if(meetinglist[i].role == 'host') {
            return meetinglist[i]
        }
    }
}

async function configureApp(){
    let host
    const configResponse = await zoomSdk.config({
      version: "0.16",
      popoutSize: {width: 480, height: 360},
      capabilities: ["shareApp", "getMeetingParticipants", "onReaction"]
    })
    console.log(configResponse)
    const myapis = await zoomSdk.getSupportedJsApis();
    console.log(myapis)
    const meetings = await zoomSdk.getMeetingParticipants()
    console.log(meetings.participants)
    host = lookForHost(meetings.participants)
    const meetingSDK = await zoomSdk.getMeetingContext();
    console.log(meetingSDK)
    var sound = new Howl({
      src: ['static/applause.mp3']
    });
    // zoomSdk.onParticipantChange((event) => {
    //     host = lookevent.participants[0] // this is the host
    //   });
    zoomSdk.onReaction(function(evt){
        console.log(evt)
        console.log(host)
        if (evt.participantUUID == host.participantUUID){
            if (evt.type == 'clap'){
                console.log("playing sound")
                sound.play()
                sound.fade(1.0, 0.0, 4000)
            }
        } else {
            if (evt.type == 'clap') {
                console.log('show the feedback to the clapper')
                document.getElementById("message").innerHTML = 'You are clapping for the host! They are hearing applause sounds now!'
                setTimeout(function(){
                    document.getElementById("message").innerHTML = ''
                }, 2000)
            }
        }
    })
    return configResponse
}


configureApp()