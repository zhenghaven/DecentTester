#include <jni_md.h>

namespace Decent
{

	namespace DhtClient
	{
		class DhtClientApp;

		JNIEXPORT void* JNICALL Initialize();
		JNIEXPORT DhtClientApp* JNICALL GetNewDhtClientApp();
	}
}
