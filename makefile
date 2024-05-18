build_whl:
	python setup.py bdist_wheel
install:
	pip install dist/*.whl
clean:
	rm -rf build dist *.egg-info
