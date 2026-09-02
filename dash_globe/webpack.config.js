const path = require('path');
const webpack = require('webpack');
const WebpackDashDynamicImport = require('@plotly/webpack-dash-dynamic-import');
const packagejson = require('./package.json');

const dashLibraryName = packagejson.name.replace(/-/g, '_');

module.exports = (env, argv) => {

    let mode;

    const overrides = module.exports || {};

    // if user specified mode flag take that value
    if (argv && argv.mode) {
        mode = argv.mode;
    }

    // else if configuration object is already set (module.exports) use that value
    else if (overrides.mode) {
        mode = overrides.mode;
    }

    // else take webpack default (production)
    else {
        mode = 'production';
    }

    let filename = (overrides.output || {}).filename;
    if(!filename) {
        const modeSuffix = mode === 'development' ? 'dev' : 'min';
        filename = `${dashLibraryName}.${modeSuffix}.js`;
    }

    const entry = overrides.entry || {main: './src/lib/index.js'};

    // Keep local source maps for debugging, but the Python package no longer
    // ships the multi-MB .map files (see MANIFEST.in / package_data).
    const devtool = overrides.devtool || (mode === 'development' ? 'eval-source-map' : 'source-map');

    const externals = ('externals' in overrides) ? overrides.externals : ({
        react: 'React',
        'react-dom': 'ReactDOM',
        'plotly.js': 'Plotly',
        'prop-types': 'PropTypes',
    });

    return {
        mode,
        entry,
        output: {
            path: path.resolve(__dirname, dashLibraryName),
            chunkFilename: '[name].js',
            filename,
            library: dashLibraryName,
            libraryTarget: 'window',
        },
        devtool,
        devServer: {
            static: {
                directory: path.join(__dirname, '/')
            }
        },
        externals,
        module: {
            rules: [
                {
                    test: /\.jsx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                    },
                },
                {
                    test: /\.css$/,
                    use: [
                        {
                            loader: 'style-loader',
                        },
                        {
                            loader: 'css-loader',
                        },
                    ],
                },
            ],
        },
        optimization: {
            splitChunks: {
                cacheGroups: {
                    // Pull the heaviest vendor graphs into separately cached
                    // async chunks so DashGlobe updates stay smaller and the
                    // browser can download/parse Three / H3 in parallel.
                    three: {
                        test: /[\\/]node_modules[\\/]three[\\/]/,
                        name: 'async-three',
                        chunks: 'async',
                        priority: 30,
                        enforce: true,
                    },
                    h3: {
                        test: /[\\/]node_modules[\\/]h3-js[\\/]/,
                        name: 'async-h3',
                        chunks: 'async',
                        priority: 25,
                        enforce: true,
                    },
                    globeVendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: 'async-globe-vendor',
                        chunks: 'async',
                        priority: 10,
                        minSize: 40_000,
                    },
                    async: {
                        chunks: 'async',
                        minSize: 0,
                        priority: 0,
                        name(module, chunks, cacheGroupKey) {
                            return `${cacheGroupKey}-${chunks[0].name}`;
                        }
                    },
                    shared: {
                        chunks: 'all',
                        minSize: 0,
                        minChunks: 2,
                        name: 'dash_globe-shared'
                    }
                }
            }
        },
        plugins: [
            new WebpackDashDynamicImport(),
            new webpack.SourceMapDevToolPlugin({
                filename: '[file].map',
                exclude: ['async-plotlyjs']
            })
        ]
    }
};
