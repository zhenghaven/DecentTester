#pragma once

#include <cstdint>

namespace Decent
{
	namespace Dht
	{
		namespace EncFunc
		{
			namespace App
			{
				typedef uint8_t NumType;
				constexpr NumType k_findSuccessor = 0;
				constexpr NumType k_getData       = 1;
				constexpr NumType k_setData       = 2;
				constexpr NumType k_delData       = 3;
			}
		}
	}
}
