
module DashGlobe
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.10"

include("jl/dashglobe.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "dash_globe",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "async-DashGlobe.js",
    external_url = "https://unpkg.com/dash_globe@0.0.10/dash_globe/async-DashGlobe.js",
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-three.js",
    external_url = nothing,
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-h3.js",
    external_url = nothing,
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-globe-vendor.js",
    external_url = nothing,
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_globe.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
