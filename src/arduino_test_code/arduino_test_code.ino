int inPin = 7;
int val = 0;
int pulseCount = 0;
bool up = false;

void setup(){
  pinMode(inPin, INPUT);
  Serial.begin(9600);
}

void loop(){
  val = digitalRead(inPin);
  if (up == false && val == HIGH){
    up=true;
  }
  else if (up == true && val == LOW){
    up = false;
    pulseCount += 1;
  }
  Serial.println(pulseCount);
}