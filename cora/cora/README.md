**Build & Run (Eigenvector & Katz implementations)**

- Compile (requires a C++11-compatible compiler such as `g++`):

	```powershell
	g++ -O2 -std=c++11 eigenc.cpp -o eigenc
	g++ -O2 -std=c++11 katz.cpp -o katz
	```

- Run Eigenvector centrality (outputs `eigenc_output.csv`):

	```powershell
	.\eigenc.exe .\cora.cites
	```

- Run Katz centrality (outputs `katz_output.csv`). You may optionally pass an `alpha` value; otherwise alpha is chosen as `0.85 / spectral_radius`:

	```powershell
	.\katz.exe .\cora.cites [alpha]
	```

**Plotting / Analysis**

We provide `plot_results.py` which joins the two CSV outputs and creates a scatter plot `centrality_scatter.png` comparing the centralities.

Requires Python packages `pandas` and `matplotlib`:

	```powershell
	pip install pandas matplotlib
	python .\plot_results.py
	```

The scripts output the top-10 nodes for each centrality and a Pearson correlation, which helps compare how the two centralities rank nodes (useful for distinguishing "foundational" vs "frontier" papers).
