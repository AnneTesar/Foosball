import org.opencv.videoio.VideoCapture;

public class Testing {
public Testing(){
		
	}
	
    public int testing(){
    	VideoCapture cap;
    	cap = new VideoCapture(0);
    	if(!cap.isOpened())
    	{
    		return -1;
    	}
//    	try {
//			wait(10);
//		} catch (InterruptedException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}
    	
    	cap.release();
    	
    	return 0;
    }

}