// SPDX-FileCopyrightText: Copyright 2026 bbport contributors
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include <vector>

#include "common/types.h"

namespace Bbport {

// BBSC's fast sign (http.cpp): the guest's sign body with the host's map written in, asked of the
// BBSC mod (bbsc.dll export BbscRewriteSummonBody) once it knows the host. False: no mod, or the
// body is already right.
bool BbscRewriteSummonBody(std::vector<u8>& body);

} // namespace Bbport
