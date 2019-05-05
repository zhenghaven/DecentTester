#include <jni_md.h>

namespace Decent
{

	namespace DhtClient
	{
		struct DhtClientAppPkg;

		JNIEXPORT void* JNICALL Initialize();
		JNIEXPORT DhtClientAppPkg* JNICALL GetNewDhtClientAppPkg(size_t cntPoolSize);
	}
}
