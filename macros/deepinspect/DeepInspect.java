import android.util.Log;
import java.lang.reflect.*;
import java.util.ArrayList;

class DeepInspect {
    public DeepInspect() {
    }

    public ArrayList<Object> findObjects(Object rootObj, String classname, int depth) {
        ArrayList<Object> result = new ArrayList<Object>();

        if (depth == 0)
            return result;

        Class<?> c = rootObj.getClass();
        do {
            for (Field f : c.getDeclaredFields()) {
                try {
                    f.setAccessible(true);
                    if (f.get(rootObj) != null)
                    {
                        if (f.get(rootObj).getClass().getName().equals(classname))
                            result.add(f.get(rootObj));
                        result.addAll(this.findObjects(f.get(rootObj), classname, depth-1));
                    }
                } catch(IllegalArgumentException e) {
                    continue;
                } catch(IllegalAccessException e2) {
                    continue;
                }
            }
            c = c.getSuperclass();
        } while (c != null);
        return result;
    }

    public ArrayList<Object> findObjects(Object rootObj, String classname) {
        return findObjects(rootObj, classname, 3);
    }
}
