import os
import shutil
import platform
import copy
import pytest
import flopy
fm = flopy.modflow
mf6 = flopy.mf6
from mfsetup import MF6model, MFnwtModel
from ..fileio import exe_exists, load_cfg
from ..utils import get_input_arguments


@pytest.fixture(scope="session")
def project_root_path():
    filepath = os.path.split(os.path.abspath(__file__))[0]
    return os.path.normpath(os.path.join(filepath, '../../'))


@pytest.fixture(scope="session")
def bin_path(project_root_path):
    bin_path = os.path.join(project_root_path, "bin")
    if "linux" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "linux")
    elif "darwin" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "mac")
    else:
        bin_path = os.path.join(bin_path, "win")
    return bin_path


@pytest.fixture(scope="session")
def mf6_exe(bin_path):
    _, version = os.path.split(bin_path)
    exe_name = 'mf6'
    if version == "win":
        exe_name += '.exe'
    return os.path.join(bin_path, exe_name)


@pytest.fixture(scope="session")
def mfnwt_exe(bin_path):
    _, version = os.path.split(bin_path)
    exe_name = 'mfnwt'
    if version == "win":
        exe_name += '.exe'
    return os.path.join(bin_path, exe_name)


@pytest.fixture(scope="session")
def demfile(project_root_path):
    return project_root_path + '/mfsetup/tests/data/shellmound/rasters/meras_100m_dem.tif'


@pytest.fixture(scope="session")
def pfl_nwt_test_cfg_path(project_root_path):
    return project_root_path + '/mfsetup/tests/data/pfl_nwt_test.yml'


@pytest.fixture(scope="function")
def pfl_nwt_cfg(pfl_nwt_test_cfg_path):
    cfg = load_cfg(pfl_nwt_test_cfg_path)
    # add some stuff just for the tests
    cfg['gisdir'] = os.path.join(cfg['model']['model_ws'], 'gis')
    return cfg


@pytest.fixture(scope="function")
def pfl_nwt(pfl_nwt_cfg):
    print('pytest fixture pfl_nwt')
    cfg = pfl_nwt_cfg.copy()
    m = MFnwtModel(cfg=cfg, **cfg['model'])
    return m


@pytest.fixture(scope="function")
def pfl_nwt_with_grid(pfl_nwt):
    print('pytest fixture pfl_nwt_with_grid')
    m = pfl_nwt  #deepcopy(pfl_nwt)
    m.setup_grid()
    return pfl_nwt


@pytest.fixture(scope="function")
def pfl_nwt_with_dis(pfl_nwt_with_grid):
    print('pytest fixture pfl_nwt_with_dis')
    m = pfl_nwt_with_grid  #deepcopy(pfl_nwt_with_grid)
    m.cfg['dis']['remake_arrays'] = True
    m.cfg['dis']['regrid_top_from_dem'] = True
    dis = m.setup_dis()
    return m


@pytest.fixture(scope="function")
def pfl_nwt_with_dis_bas6(pfl_nwt_with_dis):
    print('pytest fixture pfl_nwt_with_dis_bas6')
    bas = pfl_nwt_with_dis.setup_bas6()
    return pfl_nwt_with_dis


@pytest.fixture(scope="session")
def shellmound_cfg_path(project_root_path):
    return project_root_path + '/mfsetup/tests/data/shellmound.yml'


@pytest.fixture(scope="function")
def shellmound_datapath(shellmound_cfg_path):
    return os.path.join(os.path.split(shellmound_cfg_path)[0], 'shellmound')


@pytest.fixture(scope="module")
def shellmound_cfg(shellmound_cfg_path):
    cfg = MF6model.load_cfg(shellmound_cfg_path)
    # add some stuff just for the tests
    cfg['gisdir'] = os.path.join(cfg['simulation']['sim_ws'], 'gis')
    return cfg


@pytest.fixture(scope="function")
def shellmound_simulation(shellmound_cfg):
    cfg = shellmound_cfg.copy()
    sim = mf6.MFSimulation(**cfg['simulation'])
    return sim


@pytest.fixture(scope="function")
def shellmound_model(shellmound_cfg, shellmound_simulation):
    cfg = shellmound_cfg.copy()
    cfg['model']['simulation'] = shellmound_simulation
    cfg = MF6model._parse_modflowgwf_kwargs(cfg)
    kwargs = get_input_arguments(cfg['model'], mf6.ModflowGwf, exclude='packages')
    m = MF6model(cfg=cfg, **kwargs)
    return m


@pytest.fixture(scope="function")
def shellmound_model_with_grid(shellmound_model):
    model = shellmound_model  #deepcopy(shellmound_model)
    model.setup_grid()
    return model


@pytest.fixture(scope="function")
def shellmound_model_with_dis(shellmound_model_with_grid):
    print('pytest fixture model_with_grid')
    m = shellmound_model_with_grid  #deepcopy(pfl_nwt_with_grid)
    m.setup_tdis()
    m.cfg['dis']['remake_top'] = True
    dis = m.setup_dis()
    return m


@pytest.fixture(scope="session")
def pleasant_nwt_test_cfg_path(project_root_path):
    return project_root_path + '/mfsetup/tests/data/pleasant_nwt_test.yml'


@pytest.fixture(scope="session")
def pleasant_nwt_cfg(pleasant_nwt_test_cfg_path):
    cfg = load_cfg(pleasant_nwt_test_cfg_path)
    # add some stuff just for the tests
    cfg['gisdir'] = os.path.join(cfg['model']['model_ws'], 'gis')
    return cfg


@pytest.fixture(scope="session")
def get_pleasant_nwt(pleasant_nwt_cfg):
    print('creating Pleasant Lake MFnwtModel instance from cfgfile...')
    cfg = pleasant_nwt_cfg.copy()
    m = MFnwtModel(cfg=cfg, **cfg['model'])
    return m


@pytest.fixture(scope="session")
def get_pleasant_nwt_with_grid(get_pleasant_nwt):
    print('creating Pleasant Lake MFnwtModel instance with grid...')
    m = copy.deepcopy(get_pleasant_nwt)
    m.setup_grid()
    return m


@pytest.fixture(scope="session")
def get_pleasant_nwt_with_dis(get_pleasant_nwt_with_grid):
    print('creating Pleasant Lake MFnwtModel instance with dis package...')
    m = copy.deepcopy(get_pleasant_nwt_with_grid)  #deepcopy(pleasant_nwt_with_grid)
    m.cfg['dis']['remake_arrays'] = True
    m.cfg['dis']['regrid_top_from_dem'] = True
    dis = m.setup_dis()
    return m


@pytest.fixture(scope="session")
def get_pleasant_nwt_with_dis_bas6(get_pleasant_nwt_with_dis):
    print('creating Pleasant Lake MFnwtModel instance with dis and bas6 packages...')
    m = copy.deepcopy(get_pleasant_nwt_with_dis)
    bas = m.setup_bas6()
    return m


@pytest.fixture(scope="session")
def pleasant_nwt_setup_from_yaml(pleasant_nwt_test_cfg_path):
    m = MFnwtModel.setup_from_yaml(pleasant_nwt_test_cfg_path)
    m.write_input()
    return m


@pytest.fixture(scope="session")
def pleasant_nwt_model_run(pleasant_nwt_setup_from_yaml, mfnwt_exe):
    m = copy.deepcopy(pleasant_nwt_setup_from_yaml)
    m.exe_name = mfnwt_exe
    success = False
    if exe_exists(mfnwt_exe):
        success, buff = m.run_model(silent=False)
        if not success:
            list_file = m.lst.fn_path
            with open(list_file) as src:
                list_output = src.read()
    assert success, 'model run did not terminate successfully:\n{}'.format(list_output)
    return m


@pytest.fixture(scope="function")
def pleasant_nwt(get_pleasant_nwt):
    m = copy.deepcopy(get_pleasant_nwt)
    return m


@pytest.fixture(scope="function")
def pleasant_nwt_with_grid(get_pleasant_nwt_with_grid):
    m = copy.deepcopy(get_pleasant_nwt_with_grid)
    return m


@pytest.fixture(scope="function")
def pleasant_nwt_with_dis(get_pleasant_nwt_with_dis):
    m = copy.deepcopy(get_pleasant_nwt_with_dis)
    return m


@pytest.fixture(scope="function")
def pleasant_nwt_with_dis_bas6(get_pleasant_nwt_with_dis_bas6):
    m = copy.deepcopy(get_pleasant_nwt_with_dis_bas6)
    return m


@pytest.fixture(scope="function")
def full_pleasant_nwt(pleasant_nwt_setup_from_yaml):
    m = copy.deepcopy(pleasant_nwt_setup_from_yaml)
    return m


@pytest.fixture(scope="function")
def full_pleasant_nwt_with_model_run(pleasant_nwt_model_run):
    m = copy.deepcopy(pleasant_nwt_model_run)
    return m


@pytest.fixture(scope="session", autouse=True)
def tmpdir(project_root_path):
    folder = project_root_path + '/mfsetup/tests/tmp'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    return folder


# fixture to feed multiple model fixtures to a test
# https://github.com/pytest-dev/pytest/issues/349
@pytest.fixture(params=['shellmound_model_with_dis',
                        'pfl_nwt_with_dis_bas6'])
def models_with_dis(request,
                    shellmound_model_with_dis,
                    pfl_nwt_with_dis_bas6):
    return {'shellmound_model_with_dis': shellmound_model_with_dis,
            'pfl_nwt_with_dis_bas6': pfl_nwt_with_dis_bas6}[request.param]


# fixture to feed multiple model fixtures to a test
# https://github.com/pytest-dev/pytest/issues/349
@pytest.fixture(params=['mfnwt_exe',
                        'mf6_exe'])
def modflow_executable(request, mfnwt_exe, mf6_exe):
    return {'mfnwt_exe': mfnwt_exe,
            'mf6_exe': mf6_exe}[request.param]


