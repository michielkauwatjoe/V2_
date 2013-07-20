import oscP5.*;
import netP5.*;
  
OscP5 oscP5;
NetAddress myRemoteLocation;

int speed_acc = 0;
int x_acc = 0;
int y_acc = 0;
int z_acc = 0;
int speed_mag = 0;
int x_mag = 0;
int y_mag = 0;
int z_mag = 0;

String host = "127.0.0.1";
int port = 12000;


void setup() {

  size(400,400, P3D);
  frameRate(12);
  colorMode(RGB, 255, 255, 255);
  
  /* this osc server/client */
  oscP5 = new OscP5(this, 12000);

  /* Server application. */
  myRemoteLocation = new NetAddress("127.0.0.1", 9999); // Set to application ip, port always stays the same.
  register();
}

void register() {
  /* Function for registering to pillow server application. */
  
  OscMessage myMessage = new OscMessage("/softn/add");
  myMessage.add(host);
  myMessage.add(port);
  
  /* send the message */
  oscP5.send(myMessage, myRemoteLocation); 
}


void oscEvent(OscMessage theOscMessage) {
  /* All incoming osc message are forwarded to this method. */

  if(theOscMessage.addrPattern().equals("/softn/laban")) {
        labanEvent(theOscMessage);
  }
  else if(theOscMessage.addrPattern().equals("/softn/pressure")) {
        pressureEvent(theOscMessage);
  }  
  else if(theOscMessage.addrPattern().equals("/softn/mag")) {
        magEvent(theOscMessage);
  }
  else if(theOscMessage.addrPattern().equals("/softn/acc")) {
        accEvent(theOscMessage);
  }
  else {
     print("unknown OSC address ");
     println(theOscMessage.addrPattern()); 
  }


}


void labanEvent(OscMessage theOscMessage) {
   String pillow_name = theOscMessage.get(0).stringValue();
   String gesture_name = theOscMessage.get(1).stringValue();
}


void pressureEvent(OscMessage theOscMessage) {
  String pillow_name = theOscMessage.get(0).stringValue();
  int intensity = theOscMessage.get(1).intValue();
  int area = theOscMessage.get(2).intValue();
}

void magEvent(OscMessage theOscMessage) {
  
  // The first argument is for the source the source.
  String pillow_name = theOscMessage.get(0).stringValue();
  
  // Added speed for x, y and z.
  speed_mag = theOscMessage.get(1).intValue();
  
  // Seperate magnetometer values.  
  x_mag += theOscMessage.get(2).intValue();
  y_mag += theOscMessage.get(3).intValue();
  z_mag += theOscMessage.get(4).intValue();
}


void accEvent(OscMessage theOscMessage) {
  
  // The first argument is for the source the source.
  String pillow_name = theOscMessage.get(0).stringValue();
  
  // Added speed for x, y and z.
  speed_acc = theOscMessage.get(1).intValue();
  
  // Seperate accelerometer values.
  x_acc = theOscMessage.get(2).intValue();
  y_acc = theOscMessage.get(3).intValue();
  z_acc = theOscMessage.get(4).intValue();
}


void draw() 
{ 
  background(255);

  // Floating box.
  pushMatrix();
  translate(width/2-25+x_acc, height/2-25+y_acc, z_acc);
  rotateY(0.3 + y_mag/4);
  rotateX(-0.1 + x_mag/4);
  rotateZ(z_mag/4);
  fill(200, 100);
  stroke(50, 100);
  box(50, 50, 50); 
  popMatrix();    
 
 
 // Floor.
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3, 3*height/4, 0);
  fill(200, 150);
  stroke(255, 0);
  box(600, 1, 400);
  popMatrix();

  // Accelerometer speed offset.
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3-100, 3*height/4 - speed_acc/2, 0);
  fill(255, 255, 0, 150);
  box(50, speed_acc, 50);
  popMatrix();

  // Magnetometer speed offset.
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3-100, 3*height/4 - speed_mag/2, -50);
  fill(255, 200, 0, 150);
  box(50, speed_mag, 50);
  popMatrix();
 
  // Accelerometer dimension offsets.
 
  // x offset.
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3, 3*height/4 - x_acc/2, 0);
  fill(0, 0, 255, 150);
  box(50, x_acc, 50);
  popMatrix();

  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3 + 50, 3*height/4 - y_acc/2, 0);  
  fill(0, 255, 0, 150);
  box(50, y_acc, 50);
  popMatrix();
  
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);  
  translate(width/3 + 100, 3*height/4 - z_acc/2, 0);  
  fill(255, 0, 0, 150);
  box(50, z_acc, 50);
  popMatrix();
  
  // Magnetometer dimension offsets.
 
  // x offset.
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3, 3*height/4 - x_mag/2, -50);
  fill(0, 0, 200, 150);
  box(50, x_mag, 50);
  popMatrix();

  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);
  translate(width/3 + 50, 3*height/4 - y_mag/2, -50);  
  fill(0, 200, 0, 150);
  box(50, y_mag, 50);
  popMatrix();
  
  pushMatrix();
  rotateY(0.3);
  rotateX(-0.1);  
  translate(width/3 + 100, 3*height/4 - z_mag/2, -50);  
  fill(200, 0, 0, 150);
  box(50, z_mag, 50);
  popMatrix();
} 
