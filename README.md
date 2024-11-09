# Omnipresence

An ecosystem which works towards women saftey and empowerment. This ecosystem is powered by several products whose core objective is women safety.

### Products

- SafeScape
- Mobile Application (to be used while in danger)
- WearOS Application
- App for women empowerment content (training videos, counselling etc.) (Planned as future update)

## SafeScape

 AI Software that detects risky situations for women and potential assaults using CCTV footage and sends real time alerts to authorities.

- CCTV cameras capture continuous video footage.
- Edge devices (e.g., NVIDIA Jetson, Google Coral DevBoard) process the video streams in real-time using computer vision algorithms.
- The system detects safety threats such as:
	1. Lone Woman
	2. Woman surrounded by Men
	3. SOS Gestures
- Upon threat detection, the system logs details (alert type, description, camera ID, timestamp, intensity, and location). 


## Mobile Application

Provide women with a mobile-based safety tool that offers real-time alerts, safe route navigation, and a panic button, with added integration to the CCTV system and wearable devices

### High Priority Features
---

- **Offline Mode for Safety Features**: Allow key features such as SOS alerts and location tracking to work offline or in low-connectivity environments by sending emergency signals through SMS or Bluetooth. Ensures that users can still access safety features in areas with poor internet connectivity.

### Key Features:
---

1. **Real-time Alerts**: Receive notifications from both ML-based CCTV analysis and crowdsourced data about crime hotspots or ongoing incidents.
2. **Safe Route Navigation**: Suggest routes that avoid areas flagged as unsafe, using a combination of CCTV analysis and crowdsourced data.
3. **SOS Alerts**: Users can trigger emergency alerts that send their location to pre-determined contacts and authorities. The app can integrate with WearOS to trigger an alert from the wearable device.
4. **Crowdsourced Safety Maps**: Leverage data from users to create real-time heatmaps of unsafe areas and share this data with others.
5. **Incident Reporting**: Users can anonymously report incidents or suspicious activities, contributing to the overall safety of the community.
6. **Panic Mode with Camera Activation**: If panic mode is triggered, the camera can automatically start recording video, and the footage can be sent to emergency contacts. Provides evidence in case of a crime and enhances the likelihood of catching perpetrators.
7. **Geofencing for Dangerous Zones**: Use geofencing to automatically alert users when they are entering high-risk areas or zones flagged by other users or authorities.
Benefit: Prevents women from unknowingly walking into unsafe areas and allows for real-time decision-making.
8. **AI-Powered Threat Prediction & Risk Assessment**: Implement an AI-driven model that predicts potential threats based on historical crime data, time of day, and user behavior. Alerts women in advance about risky areas or situations, helping them avoid dangerous places or take precautionary actions.
9. **Sentiment Analysis for Real-Time Emotion Detection through audio**: Use AI for sentiment analysis to detect distress in audio, triggering emergency responses. This allows the system to automatically detect unsafe situations even if the user cannot manually send an alert.

### Integration with the Ecosystem:
---

1. **CCTV Integration**: Users will receive alerts from the ML-based CCTV analysis system if potential threats are detected nearby.
2. **WearOS Integration**: Sync with wearable devices for easy, hands-free panic button access and real-time safety data.
3. **Smart Navigation**: The app can use crowdsourced data, public transport schedules, and CCTV data to provide users with the safest routes to their destinations.

## WearOS Application

A wearable device that offers immediate access to safety features (panic button, location tracking) and syncs with the mobile app for seamless safety and monitoring.

### Key Features:
---

1. **Panic Button**: A one-tap emergency button that sends alerts and real-time location to pre-determined contacts and authorities.
2. **Biometric Monitoring**: Track heart rate, stress levels, and sudden changes in behavior. If abnormal readings are detected (e.g., increased heart rate due to stress), the system can trigger an SOS alert.
3. **Voice-Activated Commands**: Allow users to trigger alerts via voice commands if they are unable to physically press the button.
4. **Safe Area Notifications**: Notify users if they are entering or leaving a high-risk zone based on real-time data from the app and CCTV analysis.
5. **Integration with Public Transport**: Use NFC or GPS to trigger alerts if a user boards a bus or train flagged as potentially unsafe (based on public reports).
6. **Sync with App and CCTV**: Continuously sync with the mobile app to provide alerts, receive updates, and track the user's location.

### Integration with the Ecosystem:
---

1. **App Integration**: Sync with the women’s safety app for seamless access to safety features and automatic emergency contact notifications.
2. **CCTV Integration**: Receive alerts from the ML-based CCTV system regarding nearby threats or ongoing incidents.
3. **Biometric Data Sync**: Sync biometric data to both the mobile app and the analytics system to detect stress or distress signals and automatically trigger safety responses.

## How These Products Work Together in the Ecosystem:

1. **ML-based CCTV Analysis**: Detects threats and sends alerts to both authorities and app users in the vicinity, improving safety in public places.
2. **Mobile App**: Offers comprehensive features like safe route navigation, crowdsourced safety maps, and quick access to alerts from both the CCTV system and WearOS device. It also serves as the central hub for reporting incidents and receiving notifications.
3. **WearOS Device**: Acts as a wearable extension of the app, allowing for quick SOS alerts, real-time monitoring, and hands-free interaction. It’s ideal for situations where users may not have immediate access to their phones.

## Future Updates

- AI-driven Rehabilitation: Leverage AI to offer personalized mental health resources and legal guidance for victims, as well as educational content for rehabilitation of perpetrators.
- Multi-Language Support & Localization: Add support for multiple languages and localized safety data so that the app can be used in different regions and cultures.
