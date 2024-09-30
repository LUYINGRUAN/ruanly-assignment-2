let mcentroids = [];
// ONE GRAPH ONLY
const margin = {top: 10, right: 30, bottom: 30, left: 60},
	width = 600 - margin.left - margin.right,
	height = 550 - margin.top - margin.bottom;

// append the svg object to the body of the page
const svg = d3.select("#scatterChart")
	.append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", `translate(${margin.left}, ${margin.top})`);

const vizobj = document.getElementById("viz");
vizobj.addEventListener("click",(event)=> {
	var jinit = document.getElementById("init_m");
	if (jinit.value == "Manual") {
		var mouseX = parseInt(event.clientX);
		var mouseY = parseInt(event.clientY);
		var mdata = [[mouseX - 710, mouseY-360]];
		console.log(mdata);
		svg.append('g')
			.selectAll("dot")
			.data(mdata)
			.join("circle")
			.attr("cx", function (d) { return d[0]; })
			.attr("cy", function (d) { return d[1]; })
			.attr("r", 10)
			.attr("fill", "red")
		//.attr("transform", `translate(${margin.left}, ${margin.top})`);
		mcentroids.push(mdata[0]);
		var nclust = document.getElementById("n_clust");
		var numc = mcentroids.length;
		nclust.value = numc;
		nclust.setAttribute("value", numc);
		console.log(mcentroids);
		//.style("fill", "#69b3a2")
		//.attr("transform", "translate(" + mouse[0] + "," + mouse[1] + ")scale(0)")
	} else {
		mcentroids = [];
	}

});

const d3cmap = d3.scaleSequential(d3.interpolateRainbow);

function addCentroid(n) {
	do {
		svg.on("click", function () {
			var mouse = d3.pointer(this);

			console.log(mouse[0]);
			n -= 1;
		})
	} while (n > 0);
}

function drawGraph() {
	svg.selectAll("*").remove();
	d3.json("/getdata").then(function(data) {
	console.log("data");
	console.log(data);	
	// Add X axis
	const x = d3.scaleLinear()
	.domain([-10, 10])
	.range([ 0, width ]);
	svg.append("g")
	.attr("transform", `translate(0, ${height / 2})`)
	.call(d3.axisBottom(x));

	// Add Y axis
	const y = d3.scaleLinear()
	.domain([-10, 10])
	.range([ height, 0]);
	svg.append("g")
	.attr("transform", `translate(${width / 2}, 0)`)
	.call(d3.axisLeft(y));


	// Add dots
	svg.append('g')
	.selectAll("dot")
	.data(data)
	.join("circle")
		.attr("cx", function (d) { return x(d[0]); } )
		.attr("cy", function (d) { return y(d[1]); } )
		.attr("r", 3)
		.attr("fill", function (d) { return d3cmap(d[2]);})
		//.style("fill", "#69b3a2")			
	});
};


function drawCentroids() {
	d3.json("/getcentroids").then(function(data) {
	console.log("centroids");
	console.log(data);
	const x = d3.scaleLinear()
	.domain([-10, 10])
	.range([ 0, width ]);
	svg.append("g")
	.attr("transform", `translate(0, ${height / 2})`)
	.call(d3.axisBottom(x));

	// Add Y axis
	const y = d3.scaleLinear()
	.domain([-10, 10])
	.range([ height, 0]);
	svg.append("g")
	.attr("transform", `translate(${width / 2}, 0)`)
	.call(d3.axisLeft(y));	
	
	// Add dots
	svg.append('g')
	.selectAll("rect")
	.data(data)
	.join("rect")
		.attr("x", function (d) { return x(d[0]); } )
		.attr("y", function (d) { return y(d[1]); } )
		.attr("width", 10)
		.attr("height", 10)		
		//.attr("fill", function (d) { return d3cmap[d[2]];})
		.style("fill", function (d) { return d3cmap(d[2]);})
	});
};

document.getElementById('uploadForm').addEventListener('submit', async function (event) {
	event.preventDefault();

	var activebutton = document.activeElement['value'];

	const formData = new FormData();
	const nclustInput = document.getElementById('n_clust');
	const initType = document.getElementById('init_m');
	formData.append('init_type', initType.value);
	//formData.append('centroids', JSON.stringify(centroids));
	//console.log(JSON.stringify(centroids))
	formData.append('mcentroids', JSON.stringify(mcentroids));
	formData.append('n_clust', nclustInput.value);


	let response;
	switch (activebutton) {
		case "Step Through KMeans":
			formData.append('lk1', "stepk");
			response = await fetch('/kmplus', {
				method: 'POST',
				body: formData,
			});
			break;
		case "Run to Convergence":
			formData.append('lk1', "stepall");
			response = await fetch('/converge', {
				method: 'POST',
				body: formData,
			});

			break;
		case "Generate New Dataset":
			formData.append('lk1', "gendata");
			response = await fetch('/gennew', {
				method: 'POST',
				body: formData,
			});
			break;
		case "Reset Algorithm":
			formData.append('lk1', "reset");
			response = await fetch('/reset', {
				method: 'POST',
				body: formData,
			});
			break;
	}

	drawGraph();
	drawCentroids();
	console.log(initType.value);
	//if (initType.value == "Manual") {
	//	addCentroid(parseInt(nclustInput.value));
	//}
	mcentroids = [];
});