async function configureApp(){
    const configResponse = await zoomSdk.config({
      version: "0.16",
      popoutSize: {width: 480, height: 360},
      capabilities: ["shareApp", "getMeetingParticipants"]
    })
    console.log(configResponse)
    return configResponse
}


const resp = await configureApp();
