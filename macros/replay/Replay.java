import java.lang.reflect.Field;
import java.util.Map.Entry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

/**
 * Android Action-replay implementation.
 *
 * Will look for items in the given object hierarchy that match the given
 * search value. Provides a filter function to narrow the search and a
 * modifier to set the final values.
 */
class Replay {

    /**
     * Object hierarchy root.
     */
    private Object mHaystack;

    /**
     * Fields that match the values.
     */
    private ArrayList<Field> mResults;

    /**
     * Fields that contain further results.
     */
    private HashMap<Field, Replay> mChildren;

    /**
     * Constructor
     *
     * @param haystack the search root
     * @param needle the object to search for
     * @param depth depth to deploy the object hierarchy to
     */
    public Replay(Object haystack, Object needle, int depth) {
	mResults = new ArrayList<Field>();
	mChildren = new HashMap<Field, Replay>();
	mHaystack = haystack;
	// Stop confition
	if(depth > 0) {
	    Class<?> clazz = mHaystack.getClass();
	    while (clazz != null) {
		for (Field field : clazz.getDeclaredFields()) {
		    Object value = getField(field, mHaystack);
		    if (value != null) {
			if(compareField(field, mHaystack, needle)) {
			    mResults.add(field);
			}
			else {
			    Replay child = new Replay(value, needle, depth - 1);
			    // Do not add empty children.
			    if(!child.mResults.isEmpty() ||
			       !child.mChildren.isEmpty()) {
				mChildren.put(field, child);
			    }
			}
		    }
		}
		clazz = clazz.getSuperclass();
	    }
	}
    }

    /**
     * Update the filter to narrow the search.
     *
     * @param needle the new filter value.
     */
    public void applyFilter(Object needle) {
	Iterator<Field> iter1 = mResults.iterator();
	while(iter1.hasNext()) {
	    if (!compareField(iter1.next(), mHaystack, needle)) {
		iter1.remove();
	    }
	}
	Iterator<Entry<Field, Replay>> iter2 = mChildren.entrySet().iterator();
	while(iter2.hasNext()) {
	    Entry<Field, Replay> child = iter2.next();
	    child.getValue().applyFilter(needle);
	    if(child.getValue().mResults.isEmpty() &&
	       child.getValue().mChildren.isEmpty()) {
		iter2.remove();
	    }
	}
    }

    public ArrayList<ArrayList<Field>> getResults() {
	ArrayList<ArrayList<Field>> result = new ArrayList<ArrayList<Field>>();
	for(Field field : mResults) {
	    ArrayList<Field> item = new ArrayList<Field>();
	    item.add(field);
	    result.add(item);
	}
	for(Entry<Field, Replay> child : mChildren.entrySet()) {
	    ArrayList<Field> base = new ArrayList<Field>();
	    base.add(child.getKey());
	    for(ArrayList<Field> tail : child.getValue().getResults()) {
		ArrayList<Field> concat = new ArrayList<Field>(base);
		concat.addAll(tail);
		result.add(concat);
	    }
	}
	return result;
    }

    /**
     * Set all the items to the given value.
     *
     * @param value the given value
     */
    public void set(Object value) {
	for(Field field : mResults) {
	    setField(field, mHaystack, value);
	}
	for(Entry<Field, Replay> child : mChildren.entrySet()) {
	    child.getValue().set(value);
	}
    }

    private Object getField(Field field, Object obj) {
	try {
	    field.setAccessible(true);
	    return field.get(obj);
	} catch(IllegalArgumentException e) {
	    return null;
	} catch(IllegalAccessException e) {
	    return null;
	}
    }

    private void setField(Field field, Object obj, Object value) {
	try {
	    field.setAccessible(true);
	    field.set(obj, value);
	} catch(IllegalArgumentException e) {
	} catch(IllegalAccessException e) {
	}
    }

    private boolean compareField(Field field, Object obj, Object value) {
	try {
	    return getField(field, obj).equals(value);
	} catch(Exception e) {
	    return false;
	}
    }
}
