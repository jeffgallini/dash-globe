
module DashGlobe
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1"

include("jl/''_dashglobe.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "dash_globe",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "async-DashGlobe.js",
    external_url = "https://unpkg.com/dash_globe@0.0.1/dash_globe/async-DashGlobe.js",
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-DashGlobe.js.map",
    external_url = "https://unpkg.com/dash_globe@0.0.1/dash_globe/async-DashGlobe.js.map",
    dynamic = true,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_globe.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "dash_globe.min.js.map",
    external_url = nothing,
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
