import android.util.Log;
import java.lang.reflect.*;
import java.util.ArrayList;

class Replay {

    private Object m_root;

    public class ReplaySlot {
        private Object m_obj;
        private Field m_field;
        private Object m_value;

        ReplaySlot(Object obj, Field f) {
            m_obj = obj;
            m_field = f;
            m_field.setAccessible(true);
            m_value = getValue();
        }

        public Object getObject() {
            return m_obj;
        }

        public Field getField() {
            return m_field;
        }

        public boolean wasModified() {
            return (this.getValue() != m_value);
        }

        public boolean equals(Object obj) {
            return (obj.equals(this.getValue()));
        }

        public Object getValue() {
            try {
                return m_field.get(m_obj);
            }
            catch( IllegalAccessException exc) {
                return null;
            }
        }
    };

    private ArrayList<Replay.ReplaySlot> m_slots;

    public Replay(Object obj) {
        /* Initialize slots */
        m_slots = new ArrayList<Replay.ReplaySlot>();
        m_root = obj;
        clear();
    }

    public void clear() {
        m_slots.clear();
    }


    public void firstSearch(Object value, int depth) {
        /* Max depth reached ? */
        if (depth == 0)
            return;

        /* Otherwise, perform a recursive search */
        findObjects(m_root, value.getClass().getName(), value, depth);
    }


    public void UpdateOrAdd(Object obj, Field f) {
        for (Replay.ReplaySlot rs : m_slots) {
            if ((rs.getObject() == obj) && (f.getName().equals(rs.getField().getName()))) {
                return;
            }
        }
        m_slots.add(new Replay.ReplaySlot(obj, f));
    }

    public ArrayList<Replay.ReplaySlot> getSlots() {
        return m_slots;
    }

    public void findObjects(Object rootObj, String classname, Object value, int depth) {
        if (depth == 0)
            return;

        Class<?> c = rootObj.getClass();
        do {
            for (Field f : c.getDeclaredFields()) {
                try {
                    f.setAccessible(true);
                    if (f.get(rootObj) != null)
                    {
                        if (f.get(rootObj).getClass().getName().equals(classname) && (f.get(rootObj).equals(value))) {
                            UpdateOrAdd(rootObj, f);
                        }
                    }
                } catch(IllegalArgumentException e) {
                    continue;
                } catch(IllegalAccessException e2) {
                    continue;
                }
            }
            c = c.getSuperclass();
        } while (c != null);
        return;
    }

    public void filterSlots(Object rootObj, Object value, int depth) {
        if (depth == 0)
            return;
        for (Replay.ReplaySlot rs : m_slots) {
            if (!rs.equals(value)) {
                m_slots.remove(rs);
            }
        }
    }
}
