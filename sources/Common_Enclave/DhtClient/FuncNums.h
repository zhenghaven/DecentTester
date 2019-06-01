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
				constexpr NumType k_readData      = 1;
				constexpr NumType k_insertData    = 2;
				constexpr NumType k_updateData    = 3;
				constexpr NumType k_delData       = 4;
				//constexpr NumType k_findAtListSuc = 5;
				//constexpr NumType k_insertAttList = 6;
			}

			namespace User
			{
				typedef uint8_t NumType;
				constexpr NumType k_findSuccessor = 0;
				constexpr NumType k_readData      = 1;
				constexpr NumType k_insertData    = 2;
				constexpr NumType k_updateData    = 3;
				constexpr NumType k_delData       = 4;
				constexpr NumType k_findAtListSuc = 5;
				constexpr NumType k_insertAttList = 6;
			}

			namespace FileOpRet
			{
				typedef uint8_t NumType;
				constexpr NumType k_success  = 0;
				constexpr NumType k_nonExist = 1;
				constexpr NumType k_denied   = 2;
				constexpr NumType k_dos      = 3;
			}
		}
	}
}
