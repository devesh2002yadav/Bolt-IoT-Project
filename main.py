import det,json,time,math,statistics    //det is the file i saved as credentials of Bolt and twilio.
from boltiot import Sms,Bolt
def compute(history_data,frame_size,factor):
    if len(history_data)<frame_size:
        return None
    if len(history_data)>frame_size:
        del history_data[0:len(history_data)-frame_size]
        Mn=statistics.mean(history_data)
        variance=0
        for data in history_data:
            variance+=math.pow((data-Mn),2)
        Zn=factor*math.sqrt(variance/frame_size)
        High_bound=history_data[frame_size-1]+Zn
        Low_bound=history_data[frame_size-1]-Zn
        return [High_bound,Low_bound]
history_data=[]
min = 2
max = 600
mybolt=Bolt(det.API_KEY,det.DEVICE_ID)
sms=Sms(det.SID,det.AUTH_TOKEN,det.TO_NUMBER,det.FROM_NUMBER)
while True:
    print("===============================================================================================================")
    print("Taking the sensor value")
    response=mybolt.analogRead('A0')
    data=json.loads(response)
    if data['success']!=1:
        print("There was an error while taking the data.")
        print("This is the error:"+data['value'])
        time.sleep(10)
        continue
    try:
        sensor_value=int(data['value'])
    except Exception as e:
        print("There was an error while parsing the response:",e)
        continue
    value=sensor_value
    print("THE Current Light Intensity value is :"+str(value))
    try:
        if sensor_value>max or sensor_value<min:
            mybolt.digitalWrite('0','HIGH')
            print("Sensor value Crossed THE LIMIT")
            response=sms.send_sms("LDR SENSOR VALUE CROSSED THE LIMIT.THE CURRENT LIGHT INTENSITY VALUE IS : "+str(value))
            print("Status of SMS at Twilio is:"+str(response.status))
            time.sleep(10)
            mybolt.digitalWrite('0','LOW')
    except Exception as e:
        print("Error occured:Below are the details")
        print(e)
        time.sleep(10)
        continue
    bound=compute(history_data,det.FRAME_SIZE,det.MUL_FACTOR)
    print("--------------------------------------------------------------------------------------------------------")
    if not bound:
        count= det.FRAME_SIZE-len(history_data)
        print("Ah! Not enough data to compute Z-score.Need",count,"more data points")
        history_data.append(int(data['value']))
        time.sleep(10)
        continue
    try:
        if sensor_value> bound[0]  or sensor_value<bound[1]:
            mybolt.digitalWrite('0','HIGH')
            print("Alert! THERE IS A SUSPICIOUS ACTIVITY OUTSIDE, CHECK FOR AN INTRUDER")
            response=sms.send_sms("ALERT! THERE IS A SUSPICIOUS ACTIVITY OUTSIDE, CHECK FOR AN INTRUDER")
            print("Status of SMS at Twilio is:"+str(response.status))
            time.sleep(10)
            mybolt.digitalWrite('0','LOW')
        history_data.append(sensor_value)
    except Exception as e:
        print("Error",e)
    time.sleep(10)