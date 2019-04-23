import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Vector;

//Currently this is just a incomplete example.
public class DecentDhtClient //extends DB
{

/* 	public void init() throws DBException
	{
		
	} */

	protected native boolean initCBind();

/* 	public void cleanup() throws DBException
	{
		
	} */

	protected native boolean cleanupCBind();

	//@Override
	//public Status read(String table, String key, Set<String> fields, Map<String, ByteIterator> result)
	//{
	//	
	//}

	protected native boolean readCBind(String table, String key, Set<String> fields, Map<String, String> result);

	//@Override
	//public Status insert(String table, String key, Map<String, ByteIterator> values)
	//{
	//	
	//}

	protected native boolean insertCBind(String table, String key, Map<String, String> values);

	//@Override
	//public Status delete(String table, String key)
	//{
	//	
	//}

	protected native boolean deleteCBind(String table, String key);

	//@Override
	//public Status update(String table, String key, Map<String, ByteIterator> values)
	//{
	//	Status rtn = delete(table, key);
	//	if (rtn.equals(Status.OK)) 
	//	{
	//		return insert(table, key, values);
	//	}
	//	return rtn;
	//}

	//@Override
	//public Status scan(String table, String startkey, int recordcount, Set<String> fields, Vector<HashMap<String, ByteIterator>> result)
	//{
	//	return Status.NOT_IMPLEMENTED;
	//}
}