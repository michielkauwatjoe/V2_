 import oscP5.*;
  
OscP5 oscP5;
Pillow[] pillows = new Pillow[0];

void setup() {
  
  size(400,400);
  frameRate(25);
  
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this,12000);
  }


void draw() {
  background(255);  
}

/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  
  print("### received an osc message.");
  print(" address pattern: "+theOscMessage.addrPattern() + " ");
  println(theOscMessage.arguments());
}

class Pillow
{
  int w;
  int h;
  String name;
  
  Pillow (int iw, int ih, String iname) {
    w = iw;
    h = ih;
    name = iname;
  }

  void display() {
      rect(20, 20, w, h);
    }
  }
}
