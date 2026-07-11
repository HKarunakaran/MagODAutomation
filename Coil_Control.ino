const int IN1 = 2; 
const int IN2 = 3;
const int perp_button = 4;
const int para_button = 5;
const int perp_led = 6;
const int para_led = 7;
int status = 0; 

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(perp_button, INPUT);
  pinMode(para_button, INPUT);
  pinMode(perp_led, OUTPUT);
  pinMode(para_led, OUTPUT);

}

void loop() {
  if (Serial.available()) {
    String coil_status = Serial.readStringUntil('\n');
    coil_status.trim();
    if (coil_status == "PERP_ON"){
      perp_coil_on();
    } else if (coil_status == "PARA_ON"){
      para_coil_on();
    } else if (coil_status == "OOF"){
      out_of_field();
    } 
  }
  if(digitalRead(perp_button) == HIGH && status != 2){
    delay(30);
    if(digitalRead(perp_button) == HIGH){
      perp_coil_on();
      debounce(perp_button);
    }  
  } else if (digitalRead(para_button) == HIGH && status !=1) {
    delay(30);
    if(digitalRead(para_button) == HIGH){
      para_coil_on();
      debounce(para_button);
    }
  } else if (digitalRead(perp_button) == HIGH && status == 2){
    delay(30);
    if(digitalRead(perp_button) == HIGH){
      out_of_field();
      debounce(perp_button);
    }
  } else if (digitalRead(para_button) == HIGH && status == 1){
    delay(30);
    if(digitalRead(para_button) == HIGH){
      out_of_field();
      debounce(para_button);
    }
  }
}

void para_coil_on(){
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);
  digitalWrite(para_led, HIGH);
  digitalWrite(perp_led, LOW);
  status = 1;
}
void perp_coil_on(){
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(perp_led, HIGH);
  digitalWrite(para_led, LOW);
  status = 2;
}

void out_of_field(){
  digitalWrite(IN1, LOW);
  digitalWrite(perp_led, LOW);
  digitalWrite(para_led, LOW);
  status = 0;
}

void debounce(int x){
   while(digitalRead(x) == HIGH){
    }
    delay(30);
}
