
// ---------------------------------------------------------------------------
// REGION
// Unique per provider
// ---------------------------------------------------------------------------

CREATE CONSTRAINT region_unique IF NOT EXISTS
FOR (r:Region)
REQUIRE (r.provider, r.code) IS UNIQUE;


// ---------------------------------------------------------------------------
// AVAILABILITY ZONE
// Unique per provider + region + name
// ---------------------------------------------------------------------------

CREATE CONSTRAINT az_unique IF NOT EXISTS
FOR (az:AvailabilityZone)
REQUIRE (az.provider, az.region_code, az.name) IS UNIQUE;


// ---------------------------------------------------------------------------
// VIRTUAL NETWORK (VPC / VNet)
// Unique per provider + account + network_id
// ---------------------------------------------------------------------------

CREATE CONSTRAINT vnet_unique IF NOT EXISTS
FOR (v:VirtualNetwork)
REQUIRE (v.provider, v.account_id, v.network_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// SUBNET
// Unique per provider + account + subnet_id
// ---------------------------------------------------------------------------

CREATE CONSTRAINT subnet_unique IF NOT EXISTS
FOR (s:Subnet)
REQUIRE (s.account_id, s.subnet_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// ROUTE TABLE
// ---------------------------------------------------------------------------

CREATE CONSTRAINT route_table_unique IF NOT EXISTS
FOR (rt:RouteTable)
REQUIRE (rt.account_id, rt.route_table_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// GATEWAY
// ---------------------------------------------------------------------------

CREATE CONSTRAINT gateway_unique IF NOT EXISTS
FOR (g:Gateway)
REQUIRE (g.account_id, g.gateway_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// SECURITY BOUNDARY (SG / NSG / Firewall)
// ---------------------------------------------------------------------------

CREATE CONSTRAINT security_boundary_unique IF NOT EXISTS
FOR (sb:SecurityBoundary)
REQUIRE (sb.account_id, sb.boundary_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// IDENTITY (IAM Role / User / Service Account)
// ---------------------------------------------------------------------------

CREATE CONSTRAINT identity_unique IF NOT EXISTS
FOR (i:Identity)
REQUIRE (i.provider, i.account_id, i.identity_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// POLICY
// ---------------------------------------------------------------------------

CREATE CONSTRAINT policy_unique IF NOT EXISTS
FOR (p:Policy)
REQUIRE (p.provider, p.account_id, p.policy_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// RESOURCE (All Cloud Services)
// Unique per provider + account + resource_id
// ---------------------------------------------------------------------------

CREATE CONSTRAINT resource_unique IF NOT EXISTS
FOR (r:Resource)
REQUIRE (r.provider, r.account_id, r.resource_id) IS UNIQUE;


// ---------------------------------------------------------------------------
// Useful Indexes for Performance
// ---------------------------------------------------------------------------

// Resource type lookups (very common in AI queries)
CREATE INDEX resource_type_index IF NOT EXISTS
FOR (r:Resource)
ON (r.resource_type);


// Resource region filtering
CREATE INDEX resource_region_index IF NOT EXISTS
FOR (r:Resource)
ON (r.region);


// Account quick traversal
CREATE INDEX account_provider_index IF NOT EXISTS
FOR (a:Account)
ON (a.provider);


// Identity type filtering
CREATE INDEX identity_type_index IF NOT EXISTS
FOR (i:Identity)
ON (i.identity_type);
