import oscP5.*;
  
OscP5 oscP5;

int speed_acc = 0;
int x_acc = 0;
int y_acc = 0;
int z_acc = 0;
int speed_mag = 0;
int x_mag = 0;
int y_mag = 0;
int z_mag = 0;

void setup() {

  size(400,400, P3D);
  frameRate(12);
  colorMode(RGB, 255, 255, 255);
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this,12000);
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


/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  
   if(theOscMessage.checkTypetag("siiii")) {
      String type = theOscMessage.get(0).stringValue();

      if (type.equals("acc")) {
         speed_acc = theOscMessage.get(1).intValue();
         x_acc = theOscMessage.get(2).intValue();
         y_acc = theOscMessage.get(3).intValue();
         z_acc = theOscMessage.get(4).intValue();
      }
      else if (type.equals("mag")) {
         println("mag");
         speed_mag = theOscMessage.get(1).intValue();
         x_mag += theOscMessage.get(2).intValue();
         y_mag += theOscMessage.get(3).intValue();
         z_mag += theOscMessage.get(4).intValue();
      }        
      
    }
    else {
      println("Receiving wrong OSC message format");
    }
}
